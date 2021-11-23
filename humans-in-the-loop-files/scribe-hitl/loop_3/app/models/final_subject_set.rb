class FinalSubjectSet
  include Mongoid::Document
  include Mongoid::Timestamps

  scope :by_export_field, -> (name, value, exact) do
    where({
      "export_document.export_fields" => {
        '$elemMatch' => {
          name: name,
          value: ( exact ? value : { "$regex" => /#{value}/i } )
        }
      }
    })
  end

  scope :by_export_field_range, -> (name, values) do
    m = { }
    m["$gte"] = values.first if ! values.first.nil?
    m["$lte"] = values.last if ! values.last.nil?
    where({
      "export_document.export_fields" => {
        '$elemMatch' => {
          name: name,
          value: m
        }
      }
    })
  end

  belongs_to :project
  belongs_to :subject_set
  field :name,                       type: String
  field :meta_data,                  type: Hash

  field :search_terms
  field :search_terms_by_field

  index({"subjects.assertions.confidence" => 1}, {background: true})
  index({"subjects.assertions.task_key" => 1}, {background: true})
  index({"subject_set_id" => 1}, {background: true})
  index({"project_id" => 1}, {background: true})

  index({"search_terms" => "text"})

  [:total, :complete, :awaiting_votes, :in_progress, :awaiting_transcriptions].each do |field|
    index({"subjects.assertions_breakdown.all_workflows.#{field}" => 1}, {background: true})
  end

  embeds_many :subjects, class_name: 'FinalSubject'
  embeds_one :export_document, class_name: "Export::Document"

  def build_search_terms
    update_attributes({
      search_terms: compute_fulltext_terms,
      search_terms_by_field: compute_fulltext_terms_by_field
    })
  end

  def self.export_spec_fields
    Project.current.export_document_specs.map do |spec|
      spec.spec_fields
    end.flatten
  end

  def build_export_document
    if ! Project.current.export_document_specs.blank?
      self.export_document = Export::Document.from_set self, Project.current.export_document_specs
    else
      puts "No export_document_specs configured for #{Project.current.title}"
    end
  end

  def compute_fulltext_terms
    compute_fulltext_terms_by_field.values.flatten.uniq
  end

  def compute_fulltext_terms_by_field
    subjects.map { |subject| subject.fulltext_terms_by_field }.inject({}) do |h, terms|
      terms.each do |(k,vs)|
        h[k] = [] if h[k].nil?
        h[k] += vs
      end
      h
    end
  end

  def self.assert_for_set(set, rebuild=false)
    # If final_subject_set record was built after most recent generated subject, consider skipping
    skip_update = false
    if ! rebuild && (final_ss = find_by(subject_set:set))
      subjs_updated = set.subjects.max(:updated_at)
      skip_update = final_ss.updated_at > subjs_updated
    end
    inst = find_or_create_by subject_set: set
    inst.project = set.project
    inst.meta_data = set.meta_data
    if !skip_update
      inst.update_subjects
      inst.build_search_terms
      inst.updated_at = Time.now
    end
    # rebuild the export document, in case the export specification changed
    # but no new classifications were added
    inst.build_export_document
    Rails.logger.info "Saving final subject set: #{inst.id}"
    inst.save! 
  end

  def update_subjects

    # parent subject could have been destroyed
    subjects.each do |subject|
      if subject.subject.nil?
        subject.destroy
      end
    end

    Array.new(subject_set.subjects.root).each do |subject|
      existing = subjects.find_by(subject: subject)
      if !existing or existing.updated_at.blank? or existing.updated_at < subject.updated_at
        if existing
          existing.destroy
        end
        subjects << FinalSubject.create_from_subject(subject)
      end
    end
  end

  def self.rebuild_indexes(for_project)
    # If no records yet saved, moped will error when dropping indexes
    new_export_keys = for_project.export_names.map {|(key,name)|key}
    curr_export_keys = collection.indexes
      .select {|index| index[:name].start_with?("search_terms_by_field.")}
      .map {|index| index[:name].sub("search_terms_by_field.", "").sub("_1", "")}

    if self.count != 0 and curr_export_keys.sort != new_export_keys.sort
      Rails.logger.info "Export keys changed, rebuilding index"
      collection.indexes.drop_all
    end
    for_project.export_names.each do |(key,name)|
      index({"search_terms_by_field.#{key}" => 1}, {background: true})
      index({"export_document.export_fields.name" => 1, "export_document.export_fields.value" => 1})
    end
    create_indexes
  end
end

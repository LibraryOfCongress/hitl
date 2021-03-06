class Subject
  include Mongoid::Document
  include Mongoid::Timestamps
  include Randomizer

  paginates_per 3

  scope :root, -> { where(type: 'root').asc(:order) }
  scope :active_root, -> { where(type: 'root', status: 'active').asc(:order) }
  scope :by_type, -> (type) { where(type: type) }
  scope :active_non_root, -> { where(:type.ne => 'root', :status => 'active') }
  scope :active, -> { where(status: 'active').order(subject_set_id: :asc, order: :asc) }
  scope :inactive, -> { where(status: 'inactive') }
  scope :not_bad, -> { where(:status.ne => 'bad').asc(:order)  }
  scope :visible_marks, -> { where(:status.in => ['active', 'retired'], :region.ne => nil).asc(:order)  }
  scope :complete, -> { where(status: 'complete').asc(:order)  }
  scope :by_workflow, -> (workflow_id) { where(workflow_id: workflow_id)  }
  scope :by_subject_set, -> (subject_set_id) { where(subject_set_id: subject_set_id).asc(:order)  }
  scope :by_parent_subject, -> (parent_subject_id) { where(parent_subject_id: parent_subject_id) }
  scope :by_group, -> (group_id) { where(group_id: group_id) }
  scope :user_has_not_classified, -> (user_id) { where(:classifying_user_ids.ne => user_id)  }
  scope :user_did_not_create, -> (user_id) { where(:creating_user_ids.ne => user_id)  }

  # This is a hash with one entry per deriv; `standard', 'thumbnail', etc
  field :location,                    type: Hash
  field :type,                        type: String,  default: "root" #options: "root", "secondary"
  field :status,                      type: String,  default: "active" #options: "active", "inactive", "bad", "retired", "complete", "contentious"

  field :meta_data,                   type: Hash,    default: {}
  field :classification_count,        type: Integer, default: 0
  field :random_no,                   type: Float
  field :secondary_subject_count,     type: Integer, default: 0
  field :created_by_user_id,          type: String

  # Need to sort out relationship between these two fields. Are these two fields Is this :shj
  field :retire_count,                type: Integer
  field :flagged_bad_count,           type: Integer
  field :flagged_illegible_count,     type: Integer


  # ROOT SUBJECT concerns:
  field :order,                       type: Integer
  field :name,                        type: String
  field :width,                       type: Integer
  field :height,                      type: Integer
  field :zooniverse_id

  # SECONDARY SUBJECT concerns:
  field :data,                        type: Hash
  field :region,                      type: Hash

  # Denormalized array of user ids that have classified this subject for quick filtering
  field :classifying_user_ids,        type: Array, default: []
  field :deleting_user_ids,           type: Array, default: []
  field :creating_user_ids,           type: Array, default: []

  belongs_to :workflow
  belongs_to :group
  belongs_to :parent_subject, :class_name => "Subject", :foreign_key => "parent_subject_id"
  belongs_to :subject_set, :class_name => "SubjectSet", :foreign_key => "subject_set_id"
  belongs_to :project

  has_many :child_subjects, :class_name => "Subject"
  has_many :classifications, inverse_of: :subject
  has_many :favourites

  # Classifications that generated this subject:
  has_many :parent_classifications, class_name: 'Classification', inverse_of: :child_subject

  after_create :update_subject_set_stats
  after_create :increment_parents_subject_count_by_one, :if => :parent_subject

  # Index for typical query when fetching subjects for Transcribe/Verify:
  index({workflow_id: 1, status: 1, order: 1, classifying_user_ids: 1})

  # # Index for Marking by subject set:
  index({subject_set_id: 1, status: 1})
  index({subject_set_id: 1, type: 1, order: 1})
  index({subject_set_id: 1, order: 1})
  
  # Index for fetching child subjects for a parent subject, optionally filtering by region NOT NULL
  index({parent_subject_id: 1, status: 1, region: 1})

  def created_solely_by?(user)
    created_by = created_by_user_id == user.id.to_s
    created_by ||= creating_user_ids.size == 1 && creating_user_ids.first == user.id.to_s
    created_by
  end

  def thumbnail
    location['thumbnail'].nil? ? location['standard'] : location['thumbnail']
  end

  def update_subject_set_stats
    subject_set.subject_activated_on_workflow(workflow) if ! workflow.nil? && status == 'active'
    subject_set.inc_subject_count_for_workflow(workflow) if ! workflow.nil?
    # subject_set.inc_active_secondary_subject 1 if type != 'root'
  end

  def increment_parents_subject_count_by(count)
    parent_subject.inc(secondary_subject_count: count)
  end

  def increment_parents_subject_count_by_one
    increment_parents_subject_count_by 1
  end

  def increment_retire_count_by_one
    self.inc(retire_count: 1)
    self.check_retire_by_number
  end

  def increment_flagged_bad_count_by_one
    self.inc(flagged_bad_count: 1)
    self.check_flagged_bad_count
  end

  def increment_flagged_illegible_count_by_one
    self.inc(flagged_illegible_count: 1)
    # AMS: not in place yet.
    # self.flagged_illegible_count
  end

  # Get the workflow task that generated this subject, if any
  def parent_workflow_task
    if ! (_classifications = parent_classifications.limit(1)).empty?
      _classifications.first.workflow_task
    end
  end

  def export_name
    return nil if parent_workflow.nil?

    transcribe_subject = parent_workflow.name == 'transcribe' ? self : parent_subject
    transcribe_subject.parent_workflow_task.export_name if transcribe_subject && transcribe_subject.parent_workflow_task
  end

  # find all the classifications for subject where task_key == compleletion_assesment_task
  # calculate the percetage vote for retirement (pvr)
  # if pvr is equal or greater than retire_limit, set self.status == retired.
  def check_flagged_bad_count
    if flagged_bad_count >= 3
      self.bad!
      increment_parents_subject_count_by -1 if parent_subject
    end
  end

  def percentage_for_retire
    assesment_classifications = number_of_completion_assessments
    retire_count.to_f / assesment_classifications.to_f
  end

  def number_of_completion_assessments
    count = classifications.where(task_key: "completion_assessment_task").count || 0
    count + (classifications.where(task_key: "anything_left_to_mark").count || 0)
  end


  # Retire by the number of completion assesments, follows the definition in the manual:
  # "retire_limit: Number indicating threshold for retiring the subject operated on in
  # a given workflow. Mostly relevant to Mark workflow, where retire_limit is the number
  # of times we require someone to say "There is nothing left to mark."
  # In the Transcription & Verification workflows, retire_limit is ignored in favor of
  # generates_subject_after."
  def check_retire_by_number
    if retire_count >= workflow.retire_limit
      if self.retire!
        increment_parents_subject_count_by -1 if parent_subject
      end
    end
  end


  def bad!
    status! 'bad'
    subject_set.subject_deactivated_on_workflow(workflow) if ! workflow.nil?

    # Recurse badness downward!
    child_subjects.each do |child|
      if ['active','inactive'].include?(child.status)
        child.bad!
      end
    end
  end

  def retire!
    return false if status == "bad"
    return false if classifying_user_ids.length < workflow.retire_limit

    status! 'retired'
    subject_set.subject_completed_on_workflow(workflow) if ! workflow.nil?

    true
  end

  def complete!
    status! 'complete'
  end

  def activate!
    status! 'active'
    subject_set.subject_activated_on_workflow(workflow) if ! workflow.nil?
    # subject_set.inc_active_secondary_subject 1 if type != 'root'
  end

  def parent_classifications_grouped(options = { normalized: false })
    annotations = parent_classifications.map { |c| c.annotation }
    buckets = annotations.inject({}) do |h, ann|
      values = ann
      # Should we normalize values?
      if options[:normalized]
        task = workflow.nil? ? parent_subject.parent_workflow_task : parent_workflow_task
        values = Export::DocumentBuilder.normalize_annotation task, values
      end
      key = values.is_a?(Array) ? values.join('||') : values
      h[key] ||= []
      h[key] << ann

      h
    end

    buckets = buckets.sort_by { |(k,annotations)| - annotations.size }
    # puts "BUCKETS: \n#{buckets.map { |(k,v)| "#{k} => #{v.size}" }.join("  \n")}"
    buckets.map { |(k,annotations)| {ann: annotations.first, percentage: annotations.size.to_f / parent_classifications.count } }
  end

  def parent_and_descendent_classifications_grouped
    # Take peer classifications...
    classification_weights = parent_classifications_grouped_with_counts
    # and descendent classifications (those made upon child subjects) ...
    sub_classification_weights = classifications_grouped_with_counts

    # and combine them into a single hash mapping distinct annotations to vote counts:
    combined_weights = classification_weights
    total = 0
    classification_weights.keys.each do |k|
      combined_weights[k] += sub_classification_weights[k] if sub_classification_weights[k]
      total += combined_weights[k]
    end

    combined_weights = combined_weights.sort_by { |(k,v)| - v }
    combined_weights.map { |(k,v)| {ann: k, percentage: v.to_f / total, votes: v } }
  end

  def parent_classifications_grouped_with_counts
    self.class.classifications_grouped_with_counts parent_classifications
  end

  def classifications_grouped_with_counts
    self.class.classifications_grouped_with_counts classifications
  end

  def self.classifications_grouped_with_counts(classifications)
    classifications.inject({}) do |h, classification| 
      ann = classification.annotation.except(:key, :tool, :generates_subject_type)
      h[ann] = 0 if h[ann].nil?
      h[ann] += 1
      h
    end
  end

  def calculate_most_popular_parent_classification(options = { normalized: false })
    parent_classifications_grouped(options).first
  end

  def parent_workflow
    parent_classifications.limit(1).first.workflow if ! parent_classifications.empty?
  end


  def to_s
    "#{status != 'active' ? "[#{status.capitalize}] " : ''}#{workflow.nil? ? 'Final' : workflow.name.capitalize} Subject (#{type})"
  end


  # Match definition to use for omitting hidden subjects
  def self.hide_match
    {"meta_data.hide" => { "$ne": "1" }}
  end


  # Returns hash mapping distinct values for given field to matching count:
  def self.group_by_field(field, match={})
    agg = []
    agg << {"$match" => self.hide_match().merge(match) } if match
    agg << {"$group" => { "_id" => "$#{field.to_s}", count: {"$sum" =>  1} }}
    self.collection.aggregate(agg).inject({}) do |h, p|
      h[p["_id"]] = p["count"]
      h
    end
  end

  # Same as above, but restricted to Group:
  def self.group_by_field_for_group(group, field, match={})
    self.collection.aggregate([
      {"$match" => { "group_id" => group.id}.merge(self.hide_match()).merge(match)}, 
      {"$group" => { "_id" => "$#{field.to_s}", count: {"$sum" =>  1} }}

    ]).inject({}) do |h, p|
      h[p["_id"]] = p["count"]
      h
    end
  end


  def self.find_or_create_root_by_standard_url(standard_url)
    subject = Subject.find_by type: 'root', "location.standard" => standard_url
    if subject.nil?
      subject = Subject.create_root_for_url standard_url
    end
    subject
  end

  def self.create_root_for_url(standard_url)

    require 'fastimage'
    width, height = FastImage.size(standard_url,:raise_on_failure=>false, :timeout=>10.0)

    subject = Subject.create({
      type: 'root',
      subject_set: SubjectSet.create({project: Project.current, group: Project.current.groups.first, state: 'active'}),
      location: {
        standard: standard_url
      },
      width: width,
      height: height
    })
    subject.workflow = Workflow.find_by name: 'mark'
    subject.activate!
    subject
  end


  private

  def status!(status)
    self.status = status
    save
  end
end

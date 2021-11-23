class Group
  include Mongoid::Document
  include Mongoid::Timestamps

  field :key,             type: String
  field :name,            type: String
  field :description,     type: String
  field :cover_image_url, type: String
  field :external_url,    type: String
  field :meta_data,       type: Hash

  include CachedStats
  # Do this here, because for Projects this is disabled
  set_callback :find, :after, :check_and_update_stats

  update_interval 120

  belongs_to :project
  has_many :subject_sets, dependent: :destroy
  has_many :subjects

  scope :by_project, -> (project_id) { where(project_id: project_id) }

  index "project_id" => 1

  def calc_stats


    # Sum total_subjects and active_subjects counts for all workflows:
    workflow_counts = Subject.group_by_field_for_group(self, :workflow_id).inject({}) { |h, (id, c)| h[id.to_s] = {
      'active_subjects' => 0,
      'inactive_subjects' => 0,
      'total_subjects' => c
    } if id; h }
    { 'active' => 'active_subjects',
      'inactive' => 'inactive_subjects' }.each do | status, key |
      workflow_counts = Subject.group_by_field_for_group(self, :workflow_id, {status: status}).inject(workflow_counts) { |h, (id, c)| h[id.to_s] = h[id.to_s].merge({key => c}) if id; h }
    end

    total_finished = 0
    total_pending = 0
    workflow_counts.each do | _, stats |
      pending = stats['active_subjects'] + stats['inactive_subjects']
      finished = stats['total_subjects'] - pending
      stats['finished_subjects'] = finished

      total_finished += finished
      total_pending += pending
    end


    ret = {
      total_finished: total_finished,
      total_pending: total_pending,
      completeness: (total_pending > 0 || total_finished > 0) ? total_finished.to_f / (total_pending + total_finished) : 0,
      workflow_counts: workflow_counts
    }

    ret
  end
end

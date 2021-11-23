class UsersController < ApplicationController
  skip_before_action :verify_authenticity_token

  respond_to :json

  def logged_in_user
    providers = User.auth_providers
    
    respond_with AuthStateSerializer.new(user: current_or_guest_user, providers: providers)
  end

  def current_email
    email = current_user.email
    respond_to do |format|
      format.json{render json: { :email => email}}
    end
  end

  def tutorial_complete

    user = require_user!
    user.tutorial_complete!

    render json: AuthStateSerializer.new(user: current_or_guest_user, providers: User.auth_providers), status: 200
  end

  def delete
    # Soft delete a user to retain classifications
    # Delete all identifiable information
    user = require_user!
    if !User.find_by_password(user.email, params[:password])
      render nothing: true, status: 403
    else
      user.name = '[DELETED]'
      user.email = ''
      user.status = 'deleted'
      user.deleted_at = Time.current
      user.current_sign_in_ip = nil
      user.last_sign_in_ip = nil
      user.avatar = nil
      user.profile_url = nil

      user.save!(:validate => false)
      sign_out user

      render nothing: true, status: 204
    end
  end

  def stats
    return render text: "Guest users aren't allowed to view user statistics.", status: 403 if current_user.nil?
    mark_workflow = Workflow.find_by name: 'mark'
    transcribe_workflow = Workflow.find_by name: 'transcribe'
        
    # Assume tasks generating subjects are tasks where actual regions
    # are being placed: those subjects are most probably generated
    # for the transcribe task (this is the case in our project)
    region_tasks = mark_workflow.tasks
      .select { |task| 
        options = task.tool_config["options"]
        task.generates_subject_type ||
          options && !options.detect {|option| option["generates_subject_type"] }.nil? }
      .map { | task | task.key }

    aggregation = current_user.classifications.collection.aggregate([
      { "$lookup":
        {
          from: 'subjects',
          localField: 'subject_id',
          foreignField: '_id',
          as: 'subjects'
        }
      },
      { "$unwind": "$subjects" },
      { "$lookup":
        {
          from: 'subject_sets',
          localField: 'subjects.subject_set_id',
          foreignField: '_id',
          as: 'subject_sets'
        }
      },
      { "$unwind": "$subject_sets" },
      { "$match" => {
          "user_id" => current_user.id,
          "$or" => [
            {"workflow_id": transcribe_workflow.id },
            {
              "$and": [
                {"workflow_id": mark_workflow.id },
                {"task_key":  { "$in": region_tasks }}
              ]
            }
          ]
        }
      },
      {"$group" => {
        "_id" => {
          "subject_set_id" => '$subjects.subject_set_id',
          "subject_set_key" => '$subject_sets.key',
          "workflow_id" => '$workflow_id'
        },
        "count" => {"$sum" =>  1}
      }}
    ])

    data = Hash.new
    for aggr in aggregation
      subject_set_id = aggr['_id']['subject_set_id']
      subject_set_key = aggr['_id']['subject_set_key']
      workflow_id = aggr['_id']['workflow_id']
      data[subject_set_id] = Hash.new if data[subject_set_id].nil?
      data[subject_set_id]['key'] = subject_set_key
      data[subject_set_id][workflow_id] = 0 if data[subject_set_id][workflow_id].nil?
      data[subject_set_id][workflow_id] += aggr['count']
    end

    render json:data
  end

end

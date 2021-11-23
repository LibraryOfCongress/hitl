require 'csv'
require 'active_support'
require 'digest'

namespace :subjects do
  desc 'links a chain of rake tasks to setup a project, groups, and subjects'

  # Given a project key (aka name/title), returns the Project instance from the db:
  def project_for_key(key)

    # project_file_path = Rails.root.join('project', key, 'project.json')
    # project_hash = JSON.parse File.read(project_file_path)

    project = Project.find_by key: key
    project
  end

  task :load_groups, [:project_key] => :environment do |task, args|
    project_key = args[:project_key]
    subjects_dir = Rails.root.join('project', project_key, 'subjects')

    groups_file = Rails.root.join(subjects_dir, 'groups.csv')

    project = project_for_key project_key

    # project.groups.destroy_all

    num_groups = File.foreach(groups_file).count - 1
    puts "Groups: Creating #{num_groups} groups from groups.csv"
    CSV.foreach(groups_file, :headers=>true, :header_converters=> lambda {|f| f.strip}, :converters=> lambda {|f| f ? f.strip : nil}) do |row|
      data = row.to_hash

      group_key        = data['key'] # .downcase # is there a reason for downcasing?
      name             = data['name']
      description      = data['description']
      cover_image_url  = data['cover_image_url']
      external_url     = data['external_url']
      meta_data        = data.except('name')

      group = project.groups.find_or_create_by key: group_key
      group.update_attributes({
        name: name,
        description: description,
        cover_image_url: cover_image_url,
        external_url: external_url,
        meta_data: meta_data
      })

      puts "  Creating group #{$. - 1} of #{num_groups}: #{group_key}"
      Rake::Task['subjects:load_group_subjects'].invoke(project_key, group_key)

      Rake::Task['subjects:load_group_subjects'].reenable

    end
  end

  task :load_group_subjects, [:project_key, :group_key] => :environment do |task, args|
    project_key = args[:project_key]
    subjects_dir = Rails.root.join('project', project_key, 'subjects')
    group_file = Rails.root.join subjects_dir, "group_#{args[:group_key]}.csv"

    project = project_for_key args[:project_key]
    group = project.groups.find_by key: args[:group_key]

    mark_workflow = project.workflows.find_by(name: 'mark')

    # Loop over contents of group file, which has one subject per row

    subjects_by_set = {}
    file_hash = 'MISSING'

    puts "    Reading subjects from: #{group_file}"
    if ! File.exist? group_file
      puts "Couldn't find #{group_file}"
    else
      CSV.foreach(group_file, :headers=>true, :header_converters=> lambda {|f| f.strip}, :converters=> lambda {|f| f ? f.strip : nil}) do |row|
        data = row.to_hash
        key = data['set_key']
        key = "_autogen_set_key_#{$.}" if key.blank?
        subjects_by_set[key] ||= []
        subjects_by_set[key] << data
      end
      file_hash = Digest::SHA256.hexdigest File.read group_file
    end

    subjects_by_set.each do |(set_key, subjects)|

      data = subjects.first
      thumbnail       = data['thumbnail']
      name            = data['name']
      meta_data       = data.except('group_id', 'file_path', 'retire_count', 'thumbnail', 'width','height', 'order')

      puts "    Adding subject set: #{set_key} (#{file_hash})"
      subject_set = group.subject_sets.find_or_create_by key: set_key
      if file_hash == subject_set.file_hash
        puts "      - skipped subjects, file hash unchanged"
        next
      end
      subject_set.update_attributes({
        name: name,
        project: project,
        thumbnail: thumbnail,
        meta_data: meta_data
      })
      puts "      - saved subject set #{subject_set.thumbnail}"

      subjects.each_with_index do |subj, i|
        data = subj

        width = subj['width'].nil? ? nil : subj['width'].to_i
        height = subj['height'].nil? ? nil : subj['height'].to_i

        # If width/height not specified in CSV, autodetect:
        # use subjects:image_dimensions["project","group"] to predetermine this
        if width.nil? || height.nil?
          require 'fastimage'
          width, height = FastImage.size(subj['file_path'],:raise_on_failure=>false, :timeout=>10.0)
          puts "        - Autodetected image size: #{width} x #{height}"
        end

        # Parse order from csv if avail; otherwise default to position in csv:
        order = subj['order'].nil? ? i : subj['order'].to_i

        # add zooniverse_id if exists
        if subj.has_key?("zooniverse_id")
          meta_data["zooniverse_id"] = subj["zooniverse_id"]
        end

        # puts "      Adding subject: #{subj['file_path']}"
        # Subject.all.where("location.standard" => "https://s3.amazonaws.com/scribe.nypl.org/emigrant-records/originals/037.jpg").count
        # puts "s = SubjectSet[#{subject_set.id}].subjects.where(\"location.standard\" => \"#{subj['file_path']}\").first"
        # puts "  updating metadata: #{meta_data}"

        subject = subject_set.subjects.where("location.standard" => subj['file_path'], type: 'root').first
        new_subject = subject.nil?
        subject = subject_set.subjects.create if new_subject
        subject.update_attributes({
          location: {
            standard: subj['file_path'],
            thumbnail: subj['thumbnail']
          },
          workflow: mark_workflow,
          meta_data: meta_data,
          width: width,
          height: height,
          order: order,
          group: group
        })
        if new_subject
          subject.activate!
          puts "Added new subject: #{subject.location[:standard]}"
        end
      end

      puts "      - saved subject set file hash #{file_hash}"
      subject_set.update_attributes({
        file_hash: file_hash
      })

    end
  end
  
  task :image_dimensions, [:project_key, :group_key] => :environment do |task, args|
    project_key = args[:project_key]
    subjects_dir = Rails.root.join 'project', project_key, 'subjects'
    group_file = Rails.root.join subjects_dir, "group_#{args[:group_key]}.csv"

    subjects = []
    headers = nil

    puts "    Reading subjects from: #{group_file}"
    if ! File.exist? group_file
      puts "Couldn't find #{group_file}"
    else
      # Loop over contents of group file, which has one subject per row
      CSV.foreach(group_file, :headers=>true, :header_converters=> lambda {|f| f.strip}, :converters=> lambda {|f| f ? f.strip : nil}) do |row|
        data = row.to_hash
        headers = row.headers
        subjects << data
      end
      headers << 'width' if !headers.include? 'width'
      headers << 'height' if !headers.include? 'height'

      CSV.open(group_file, "wb") do |csv_file|
        csv_file << headers
        subjects.each_with_index do |subj, i|
          width = subj['width'].nil? ? nil : subj['width'].to_i
          height = subj['height'].nil? ? nil : subj['height'].to_i

          if width.nil? or height.nil?
            # Save updated dimensions in CSV if they haven't been set yet:
            require 'fastimage'
            width, height = FastImage.size(subj['file_path'],:raise_on_failure=>false, :timeout=>10.0)
            puts "        - Autodetected image size: #{width} x #{height}"
            subj['width'] = width
            subj['height'] = height
          end
          row = headers.map { |cell| subj[cell] }
          csv_file << row
        end
      end
    end
  end
end

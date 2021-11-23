> **Warning**

> This project is experimental and not well supported.

# Scribe-HITL

[Scribe](http://scribeproject.github.io/) is a framework for crowdsourcing the transcription of text-based documents, particularly documents that are not well suited for Optical Character Recognition. It is a collaboration between [Zooniverse](https://www.zooniverse.org/) and [The New York Public Library Labs](http://labs.nypl.org/) with generous support from [The National Endowment for the Humanities (NEH), Office of Digital Humanities](http://www.neh.gov/divisions/odh).

This version of Scribe is based on a [fork](https://github.com/UUDigitalHumanitieslab/scribeAPI) created by the [Digital Humanities Lab at Utrecht University](https://dig.hum.uu.nl/), which has additional functionality and updated dependencies for the [CEMROL crowd-sourcing project](https://skillnet.nl/cemrol/). For the Library of Congress Humans-in-the-Loop (HITL) project, AVP modified some of these customizations and developed a project for crowdsourcing structured data from the [U.S. Telephone Directory Collection](https://www.loc.gov/collections/united-states-telephone-directory-collection/about-this-collection/) Yellow Pages. This project featured five different tasks that support groud truth testing and training of machine learning processes for extracting business listing data from the Yellow Pages. Because of the limitations of Scribe, which only allows one Mark and one Transcribe task per instance, it was necessary to set up three separate instances of Scribe for this project. Workflow 1 (/loop_1) includes a Mark task where users draw boundaries around business groupings, advertisements and "telephone tips." Workflow 2 (/loop_2) includes a Mark task where users draw boundaries around business grouping headings and individual business listings, and a Transcribe task where users transcribe the text of business grouping headings. Workflow 3 (/loop_3) includes a Mark task where users draw boundaries around entities (business name, address, phone number, etc.) in a business listing and a Transcribe task where users transcribe the text of those entities.

For instructions on deploying this project, skip to [Setting up 3 Scribe instances on a fresh Ubuntu server](#setting-up-3-scribe-instances-on-a-fresh-ubuntu-server) below.

_[The sections below are copied from the Utrecht University project and may or may not apply to implementation of this particular fork.]_

## For Project Creators

Are you an organization or individual interested in using Scribe for your next crowdsourced transcription project? Start here!

* What is Scribe and is it for me? Read our [Scribe Primer](https://github.com/zooniverse/scribeAPI/wiki/Getting-started)
* Ready to set up your project? Head over to our [Project Setup page](https://github.com/zooniverse/scribeAPI/wiki/Setting-up-your-project)
* !! Use yarn instead of npm, this is needed by [rails/webpacker](https://github.com/rails/webpacker) !!

## For Contributors

Would you like to contribute to the codebase? Check out these technical resources about the Scribe framework and make your first pull request!

* [Terms and Keywords](https://github.com/zooniverse/scribeAPI/wiki/Terms-and-Keywords)
* Setting up your environment on [Mac OSX](https://github.com/zooniverse/scribeAPI/wiki/Setup-Mac-OSX), [Windows](https://github.com/zooniverse/scribeAPI/wiki/Setup-in-Windows-Vagrant), or [Unix](https://github.com/zooniverse/scribeAPI/wiki/Setup-Unix)
* [Data Model & Tools Config](https://github.com/zooniverse/scribeAPI/wiki/Data-Model-%26-Tools-Config)
* [Creating Custom Marking Tools](https://github.com/zooniverse/scribeAPI/wiki/Creating-Custom-Marking-Tools)
* [Setting up OAuth & Deploying](https://github.com/zooniverse/scribeAPI/wiki/Setting-up-OAuth-%26-Deploying)

## Dependencies and Deployment

### Software versions

* Node versions greater than 10. You might need to [use n](https://github.com/tj/n) to install and activate a specific version of Node for development. It has been tested to work in production with Node 10 and development using Node 13.

* [Yarn](https://yarnpkg.com/) is required for [Webpacker](https://github.com/rails/webpacker).

### Code changes

* In `config/mongoid.yml` changed `sessions` to `clients` .
* In `app/models/classification.rb` changed `find_and_modify` method to `find_one_and_update` .

### Environment variables -- Development

This isn't really mentioned in the [ScribeAPI wiki](https://github.com/zooniverse/scribeAPI/wiki):

* Create a file in the root of the project called `.env` .
* Use `rake secret` to create a secret key.
* Add `DEVISE_SECRET_TOKEN=yournewkey` to `.env` .
* Repeat to add `SECRET_KEY_BASE_TOKEN=anothernewkey` to `.env` .
* To specify the name of the Mongo database you want to create, set `MONGO_DB=yourdbname` 
* If you're going to start up the Puma web server (see below), add `RACK_ENV=development` and `PORT=3000` 

Also add your OAUTH keys to `.env` as mentioned [in the wiki](https://github.com/zooniverse/scribeAPI/wiki/Setting-up-OAuth-%26-Deploying).

### Deployment to Heroku

After creating your Heroku app and database as described [in the wiki](https://github.com/zooniverse/scribeAPI/wiki/Setting-up-OAuth-%26-Deploying):

* Add `DEVISE_SECRET_TOKEN` and `SECRET_KEY_BASE_TOKEN` to Heroku's environment variables, eg: `heroku config:set "DEVISE_SECRET_TOKEN=yournewkey"` 
* Add your `MONGOLAB_URI` and OAUTH credentials as described in the wiki.

The information about buildpacks in the wiki is out of date. Ignore the section about `BUILDPACK_URL` but before you deploy to Heroku run the following commands:

* `heroku buildpacks:add --index 1 heroku/nodejs` 
* `heroku buildpacks:add --index 2 heroku/ruby` 

The index values are important as Node needs to be built first, otherwise the Ruby build will fail complaining about Browserify.

### Procfile

The original repo had a non-functional `procfile` -- capitalisation matters to Heroku, so I've renamed it `Procfile` . Heroku recommends running the [Puma web server](https://devcenter.heroku.com/articles/getting-started-with-rails4#webserver), so I've just followed their instructions on what to include in the `Procfile` . If you want to test the config in your development environment, make sure you set the `RACK_ENV` and `PORT` values in your `.env` file and then use Foreman -- `foreman start` .

## Setting up 3 Scribe instances on a fresh Ubuntu server

This document outlines the work required to set up three separate Scribe rails apps on a single Ubuntu (18.04?) VM.  The codebase used for this install was a private fork provided by Sheean Spoel | Wetenschappelijk programmeur Digital Humanities | Fac. Geesteswetenschappen | Universiteit Utrecht | https://dig.hum.uu.nl

This initial install was conducted on a remote Ubuntu VM using ports 3000-3002 for the purposes of running proof-of-concept rails apps on the server.


### Initial Setup / SSH

1. Get SSH access to the server
2. Once SSH access is granted, optionally, generate an ssh key and add it to the remote.  Run `ssh-keygen` and follow the prompt, then use `ssh-copy-id` to add your public key to the remote.  You will be required to know the initial password for the login provided by the server admin who granted you ssh access.
   - `ssh-keygen`
   - `ssh-copy-id -i <path-to-new-ssh-key> <user@remote-ip>`
3. Optionally, add a block to your ssh config to make logging in a bit easier. 
   - In your `~/.ssh/config file`, add a block like the following:

    ```
   Host loop_test_server
    Hostname <remote-ip>
    User <user, e.g. ubuntu>
    IdentityFile <path-to-new-ssh-key>
    Port 22
    ```
   * You can now ssh into the server using `ssh loop_test_server`, or whatever you named the Host directive above in your config.  

### Update Ubuntu Packages

4. SSH into the server using the credential provided to you by a server admin, or, optionally, using the ssh key you generated in step 2.
5. Once you have a shell on the server, update the Ubuntu package lists, run:
```
sudo apt-get update
```

### GitHub Access on Remote (if using SSH access to repo)

6. Set up a new SSH key on the remote for GitHub access to the original repository.  If you are using HTTPS to clone your git repository, you can skip this step and the next step.
   - Generate your key: 

    ```ssh-keygen -t ed25519 -C "your_email@example.com"```
   - Start the SSH agent in the background:

    ```eval "$(ssh-agent -s)"```
   - Add your key to the agent:

    ```ssh-add ~/.ssh/id_ed25519```
7. Add your public SSH key to your GitHub account (See GitHub docs for instructions)

### Install Docker and docker-compose on Remote

8. Install Docker
   - Update apt packages and allow install over HTTPS:

    ```
    sudo apt-get install \
    apt-transport-https \    
    ca-certificates \
    curl \
    gnupg \
    lsb-release
    ```
   - Add Docker’s GPG key:

    ```
    curl -fsSL https://download.docker.com/linux/ubuntu/gpg | sudo gpg --dearmor -o /usr/share/keyrings/docker-archive-keyring.gpg
    ```
   - Set up the stable repository:

    ```
    echo \
    "deb [arch=amd64 signed-by=/usr/share/keyrings/docker-archive-keyring.gpg] https://download.docker.com/linux/ubuntu \
    $(lsb_release -cs) stable" | sudo tee /etc/apt/sources.list.d/docker.list > /dev/null
    ```
   - Update repositories again:

    ```sudo apt-get update```
   - Install Docker Engine:

    ```sudo apt-get install docker-ce docker-ce-cli containerd.io```
   - Once install is complete, add your user to the `docker` group so that you do not need privileged access to run docker commands:

    ```sudo usermod -aG docker $USER```
   - Install docker-compose:
      - Download current stable release:

        ```
        sudo curl -L "https://github.com/docker/compose/releases/download/1.28.5/docker-compose-$(uname -s)-$(uname -m)" -o /usr/local/bin/docker-compose
        ```
      - Apply executable permissions to the binary:

        ```sudo chmod +x /usr/local/bin/docker-compose```

### Install RVM and Ruby version 2.2.10 on Remote

9. Install RVM (Ruby Version Manager)
   - Install GPG keys
      - Run:

       ```
       gpg --keyserver hkp://pool.sks-keyservers.net --recv-keys 409B6B1796C275462A1703113804BB82D39DC0E3 7D2BAF1CF37B13E2069D6956105BD0E739499BDB
       ```
      - If this fails, ensure firewall / sg rules are not blocking port 11371
   - Install RVM (latest stable version):

    ```\curl -sSL https://get.rvm.io | bash -s stable```
   - Source the RVM script:

    ```source /home/`whoami`/.rvm/scripts/rvm```
10. Install Ruby version 2.2.10:

```rvm install “ruby-2.2.10”```

### Install Node, NVM, NPM, and yarn on Remote

11. Install Node.js and NPM:
   - ```sudo apt-get install nodejs```
   - ```sudo apt-get install npm```
12. Install NVM:

 ```
 curl -o- https://raw.githubusercontent.com/nvm-sh/nvm/v0.37.2/install.sh | bash
 ```
13. Install yarn (I believe this is required for webpack in this project):

 ```sudo npm install --global yarn```

14. Log out and log back into the server
15. Use nvm to install node 10:

 ```nvm install 10```

16. Check that you are now using version 10:

   - ```node --version```
   - This should show v10.xx.x.  In my case, v10.24.0

### Set up three separate Scribe projects

17. Make a working directory (relative to your home directory, for instance) and move into it
   - ```mkdir humans_in_the_loop```
   - ```cd humans_in_the_loop```
18. Clone the project using git.  Note, I cloned from the (private) fork I have been granted access to, which includes code in relatively good working order.

 ```git clone <the-git-repository>```

19. For expediency, copy this repository to three different directories.  Each of these directories will contain a separate configuration file for running the three separate instances of the project.
   - ```cp <cloned_directory> -r loop_1```
   - ```cp <cloned_directory> -r loop_2```
   - ```cp <cloned_directory> -r loop_3```

20. Your working directory should now look like this:
 ```
 ./humans_in_the_loop
 loop_1
 loop_2
 loop_3
 <cloned_directory>
 ```
21. Now that three copies of the project exist, create an archive folder in your working directory and move the original cloned directory there.
   - ```mkdir archive```
   - ```mv <cloned_directory> archive```

### Set up three containerized MongoDB instances

22. Create a `mongo` directory in your working directory and move into this directory
   - ```mkdir mongo```
   - ```cd mongo```
23. Create three separate init scripts that each mongo instance will run on startup.  It would be possible to use a single startup script against each, as well, but for the sake of complete differentiation between environments, I created three separate scripts that could be modified independently. Create a single script for now.

 ```touch init-mongo-1.js```

24. Using vim (or your preferred editor), edit this script to contain the following:
 ```
db.createUser(
  {
                user: "loop_dev",
    pwd: "loop_dev",
    roles: [
    { 
      role: "dbAdmin", 
      db: "loop_dev" 
    },
    { 
      role: "readWrite", 
      db: "loop_dev" 
    },
    ]
  }
)
 ```

25. For now, copy this file to two additional locations:
   - ```cp init-mongo-1.js init-mongo-2.js```
   - ```cp init-mongo-2.js init-mongo-3.js```

26. Create a docker-compose file for running three instances of mongo 4.
   - vim (or your preferred editor) 
    ```docker-compose.yml```
   - The docker-compose.yml file should look like this:

    ```
    version: '3'
    services:
            # yell
            ow-pages-1
            mongodb_1:
                    image: 'mongo:4.0-xenial'
                    container_name: 'mongodb_dev_1'
                    environment:
                            - MONGO_INITDB_DATABASE=loop_dev
                            - MONGO_INITDB_ROOT_USERNAME=loop_dev
                            - MONGO_INITDB_ROOT_PASSWORD=loop_dev
                    volumes:
                            - ./init-mongo-1.js:/docker-entrypoint-initdb.d/init-mongo.js:ro
                            - ./appdata_1:/data/db
                    ports:
                            - '27017-27019:27017-27019'

            # yellow-pages-2
            mongodb_2:
                    image: 'mongo:4.0-xenial'
                    container_name: 'mongodb_dev_2'
                    environment:
                            - MONGO_INITDB_DATABASE=loop_dev
                            - MONGO_INITDB_ROOT_USERNAME=loop_dev
                            - MONGO_INITDB_ROOT_PASSWORD=loop_dev
                    volumes:
                            - ./init-mongo-2.js:/docker-entrypoint-initdb.d/init-mongo.js:ro
                            - ./appdata_2:/data/db
                    ports:
                            - '27020-27022:27017-27019'

            # yellow-pages-3
            mongodb_3:
                    image: 'mongo:4.0-xenial'
                    container_name: 'mongodb_dev_3'
                    environment:
                            - MONGO_INITDB_DATABASE=loop_dev
                            - MONGO_INITDB_ROOT_USERNAME=loop_dev
                            - MONGO_INITDB_ROOT_PASSWORD=loop_dev
                    volumes:
                            - ./init-mongo-3.js:/docker-entrypoint-initdb.d/init-mongo.js:ro
                            - ./appdata_3:/data/db
                    ports:
                            - '27023-27025:27017-27019'

    volumes:
            appdata_1:
            appdata_2:
            appdata_3:
    ```

26. The docker-compose.yml file you created above will start 3 instances of MongoDB.  Each of the three instances will write data to a separate local directory mounted as a bind mount to the local `mongo` directory that we’re working in. These will be called `appdata_1`, `appdata_2`, and `appdata_3`, respectively.  **These directories will get created automatically when docker-compose starts our containers.**

27. Run your 3 mongo containers in detached mode using the docker-compose file.
   - ```docker-compose up -d```
   - This will start three separate instances of mongodb.  According to the ports configured in the docker-compose file above, these instances will be accessible from the host machine on ports 27017, 27020, and 27023, respectively.

28. Once the image has been pulled and the containers launched, confirm that they are running using: docker ps
   - You should notice three separate container instances running, with ports mapping from 27017 in each container to a respective differentiated port on the host (27017, 27020, 27023).

29. At this point, the directory structure of `/humans_in_the_loop/mongo/` should look like this. (You can run `ls -la` to check):

 ```
 ./humans_in_the_loop/mongo
 appdata_1
 appdata_2
 appdata_3
 docker-compose.yml
 init-mongo-1.js
 init-mongo-2.js
 init-mongo-3.js
 ```

### Update each mongoid.yml database configuration file

30. Update the mongoid.yml file in each application subdirectory so that each application can connect to a different instance of mongo.
   - Under production: -> clients: -> default: -> options:, add the following:

    ```
    user: loop_dev
    password: loop_dev
    auth_source: admin
    auth_mech: :scram
    ```

    (^ note the colon prefix is intentional)

   - Update the fallback database name to ‘loop_dev’ from ‘scribe_api_development’
   - Add the same for development: -> clients: -> default: -> options section.
   - Add the same for test: -> clients: -> default: -> options section.
   - After these steps are complete, each environment block in the config file should should look something like

    ```
    # mongoid.yml
    # ...
    development:
      clients:
        default:
          database: <%= ENV['MONGO_DB'].blank? ? 'loop_dev' : ENV['MONGO_DB'] %>
          hosts:
            - localhost:27017
          options:
            user: 'loop_dev'
            password: 'loop_dev'
            auth_source: admin
            auth_mech: :scram
    ```
   - Repeat this process for the remaining 2 projects, except update all instances of localhost:27107 to:
      - `localhost:27020` (for the second instance)
      - `localhost:27023` (for the third instance)


31. Copy or create the projects you would like to run into each separate directory’s `project` subdirectory. 

## Install all Ruby Gems and node dependencies in each project

32. Change directories into each of the three application directories and run bundle and yarn install.  This may take a few minutes to complete for the first application.
   - ```bundle```
   - ```yarn install```

## Create .env file for each application

33. In the root application directory for loop_1, create a .env file.  This file should have the following content:

 ```
 MONGO_DB=loop_dev
 DEVISE_SECRET_TOKEN=<devise_key_1>
 SECRET_KEY_BASE_TOKEN=<devise_key_2>
 ```

34. Replace the PORT value in each with the particular port on which the Rails app will be exposed.  In the case of our test server, this will be 3000, 3001, or 3002, for each app, respectively.

35. Replace DEVISE_SECRET_TOKEN value with a random key generated by running:

 ```bundle exec rake secret```   
 (e.g. output: 50190622c457141e602594e67dd5b81a0d264f7e43a3e720238e1cd3aeeefc34e56ceb921c22e4736e9127175af11e457585c3dcd7753b94e6429b99cb54388e)

36. Replace SECRET_KEY_BASE_TOKEN  value with a new random key by running the same command again.

37. Copy the .env file to the other two projects, e.g.
 - ```cp ./.env ../loop_2```
 - ```cp ./.env ../loop_3```

### Load Each Project

38. In the root of each application, use the custom rake task to load your project.  For example,  
 In loop_1/, we run:  
 ```rake project:load[‘yellow-pages-1’]```

### Run Each Application

39. In each project directory, run

 ```rails s -b 0.0.0.0 -p <port-for-this-instance>```

40. Visit the `<ip>:<port>` in your browser.

### Tips:

When I modified jsx files in the project, I found that I needed to clear the assets cache before re-running the Rails server.  When a request came in, assets recompiled and my changes were visible.  E.g.

- Make changes to JSX
- Stop the Rails Server (find the pid running on the port and kill it)
   - `lsof -i :3000` (or whatever port you’re running on)
   - `kill -9 <the pid from above>`
- Clear assets cache:
   - `rake tmp:cache:clear`
- Start the app again
   - `rails s -b 0.0.0.0 -p 3000` (or whatever port you want to run on)

### Changes

To the Universiteit Utrecht fork, I added stroke width and removed overlap prevention in the rectangle-tool file.  
- File: /app/assets/javascripts/components/mark/tools/rectangle-tool/index.jsx
- In this file, find the section with the comment “overlap” around line 91, in a conditional block.  I commented this block out, which returns false when there is an overlapping rectangle.
- In this file, I added constants for `STROKE_WIDTH` and SELECTED_`STROKE_WIDTH` and modified the polyline SVG element to add an attribute with a ternary value `“stroke-width=”${this.props.selected ? SELECTED_STROKE_WIDTH/scale : STROKE_WIDTH/scale }”`
- Uncertain if the json in project configs actually wires up to the stroke-width, though it does affect color.  Changing these values for stroke-width does not currently seem to have an effect.  The color comes in on a prop to the component, so perhaps this can be configured in a parent component?

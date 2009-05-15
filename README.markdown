Flix Cloud API Sample Python Library
====================================

Version: 0.2  
Date:    May 7, 2009

A sample Python client library for interacting with the [On2 Flix Cloud](http://flixcloud.com) API.

See [http://flixcloud.com/api](http://flixcloud.com/api) for more details about the API.


REGISTERING JOB REQUESTS
------------------------
Create FlixCloud.Job object, set parameters and send the request using "send" method. If registartion is successful "send" method will return True (and set "success" attribute to True). If failure occurs, "success" will be set to False and in the "error" list you will find error messages.

 **API key is required and can be found in your Dashboard at https://flixcloud.com/settings**  
 **Recipe ID or Recipe NAME is required and can be found in your Dashboard at  http://flixcloud.com/overviews/recipes**  
 **For files  (input, output, watermark) url is required. You can also set user & password if needed.


### EXAMPLE 1
    
    import FlixCloud

    job_req = FlixCloud.Job('api_key') # API key required
    job_req.recipe_id = 3   # Set recipe id or recipe name
    job_req.set_input('http://example.com/file_in.mpg') # input file location
    job_req.set_output('ftp://example.com/file_out.avi', 'user', 'password') # output file location (and user & password)
    job_req.set_watermark('http://example.com/watermark.png') #watermark file location
    job_req.send() # send request
    if job_req.success: # registration successful
        print job_req.id # registered job id
        print job_req.initialized_job_at # registered job initialization time
    else:   # registration failure
        for error in job_req.errors: # see errors
            print error

### EXAMPLE 2 (params in python dictionary)

    import FlixCloud

    params =  {
        'recipe_name' : 'mpg2avi', # recipe name can be used instead of recipe id
        'input_url' : 'http://example.com/file_in.mpg',
        'output_url' : 'ftp://example.com/output.avi',
        'output_user' : 'ftp_user',
        'output_password' : 'ftp_pass',
        'watermark_url' : 'http:///watermark.png',
        'send' : True # if send param is set to True there is no need to run send method
    }

    job_req = FlixCloud.Job('api_key', params) # API key and params are given

    if job_req.success: # registration successful
        print job_req.id # registered job id
        print job_req.initialized_job_at # registered job initialization time
    else:   # registration failure
        for error in job_req.errors: # see errors
            print error



NOTIFICATIONS
----------------------
The JobNotification class parses XML message sent from FlixCloud when a job is completed (or something went wrong).

**Notification URL must be set in https://flixcloud.com/settings**  

### EXAMPLE

    import FlixCloud

    notification = FlixCloud.JobNotification(xml_msg)

    if notification.state == 'successful_job':
        print notification.id
        print notification.output_media_file.url
        print notification.output_media_file.cost

        print notification.input_media_file.url
        print notification.input_media_file.cost
        # etc.
    elif notification.state == 'cancelled_job'
          # Action if job is cancelled
    elif notification.state ==  'failed_job'
          print notification.error_message

## Notes

Creating jobs sends HTTP requests to Flix Cloud, which may take some time. It's best to do this asynchronously in your application.

## COPYRIGHT

Copyright (c) 2009 On2 Technologies, Inc. See LICENSE for details.


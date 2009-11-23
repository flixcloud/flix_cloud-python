"""
FlixCloud API Python Library
Version: 0.2
Author: Pawel Markowski <pawmar@gmail.com>

"""

import xml.dom.minidom
import httplib

def xml_str(doc, tag, parentTag=None, debug=False):
    """Returns string from xml document from tag (and parentTag)"""
    if parentTag:
        try:
            el = doc.getElementsByTagName(parentTag)[0]
        except IndexError:
            if debug:
                print 'No such parent tag: %s' % parentTag
            return None
        doc = el
    try:
        result = doc.getElementsByTagName(tag)[0].firstChild.data.strip()
    except IndexError:
        if debug:
            print 'No such tag: %s' % tag
        return None
    return result

def xml_int(doc, tag, parentTag=None, debug=False):
    """Returns int from xml document from tag (and parentTag)."""
    if parentTag:
        try:
            el = doc.getElementsByTagName(parentTag)[0]
        except IndexError:
            if debug:
                print 'No such parent tag: %s' % parentTag
            return None
        doc = el
    try:
        result = int(doc.getElementsByTagName(tag)[0].firstChild.data)
    except IndexError:
        if debug:
            print 'No such tag: %s' % tag
        return None
    return result


class Job:
    """FlixCloud Job."""
    def __init__(self, api_key, params=None):
        #API url: https://www.flixcloud.com/jobs
        self.api_base_url = 'www.flixcloud.com'
        self.api_req_url = '/jobs'
        self.api_key = api_key

        self.recipe_id = None
        self.recipe_name = None

        self.input = None
        self.output = None
        self.watermark = None
        self.notification_url = None

        self.result = {}
        self.errors = []

        if params:
            if 'recipe_id' in params:
                self.recipe_id =  str(params['recipe_id'])
            elif 'recipe_name' in params:
                self.recipe_name = params['recipe_name']

            if 'input_url' in params:
                self.set_input(params['input_url'],
                                params.get('input_user', None),
                                params.get('input_password', None))

            if 'output_url' in params:
                self.set_output(params['output_url'],
                                params.get('output_user', None),
                                params.get('output_password', None))

            if 'watermark_url' in params:
                self.set_watermark(params['watermark_url'],
                                params.get('watermark_user', None),
                                params.get('watermark_password', None))

            if 'notification_url' in params:
       self.set_notification_url(params['notification_url'])

            if 'send' in params:
                if params['send']:
                    self.send()

    def set_input(self, url, user=None, password=None):
        """Sets input file data."""
        self.input = JobInputFile(url, user, password)

    def set_output(self, url, user=None, password=None):
        """Sets output file data."""
        self.output = JobOutputFile(url, user, password)

    def set_watermark(self, url, user=None, password=None):
        """Sets watermark file data."""
        self.watermark = JobWatermarkFile(url, user, password)

    def set_notification_url(self, notify_url):
        """Sets the notification url"""
        self.notification_url = notify_url

    def validate(self):
        """Checks if data are correct and ready to send."""
        if not (self.recipe_id or self.recipe_name):
            self.errors.append('Either recipe_id or recipe_name is required.')
        if not self.api_key:
            self.errors.append('API key is required.')
        if not (self.input and self.output):
            self.errors.append('Input and output files are required.')

        #Validate files:
        for jobFile in (self.input, self.output, self.watermark):
            if jobFile:
                if not jobFile.valid():
                    self.errors.extend(jobFile.errors)
        
        if self.errors == []:
            return True
        else:
            return False

    def get_job_xml(self):
        """Create xml for FlixCloud job request."""
        doc = xml.dom.minidom.Document()

        api_req = doc.createElement('api-request')
        doc.appendChild(api_req)
       
        api_key = doc.createElement('api-key')
        api_key.appendChild(doc.createTextNode(self.api_key))
        api_req.appendChild(api_key)

        if self.recipe_id:
            recipe_id = doc.createElement('recipe-id')
            recipe_id.appendChild(doc.createTextNode(str(self.recipe_id)))
            api_req.appendChild(recipe_id)
        elif self.recipe_name:
            recipe_name = doc.createElement('recipe-name')
            recipe_name.appendChild(doc.createTextNode(self.recipe_name))
            api_req.appendChild(recipe_name)

   if self.notification_url: 
            notify_url = doc.createElement('notification-url')
            notify_url.appendChild(doc.createTextNode(self.notification_url))  
            api_req.appendChild(notify_url)
       
        #file-locations node
        file_locations = doc.createElement('file-locations')
        
        #input node
        if self.input:
            input = doc.createElement('input')
            input_url = doc.createElement('url')
            input_url.appendChild(doc.createTextNode(self.input.url))
            input.appendChild(input_url)

            if self.input.user and self.input.password:
                input_parameters = doc.createElement('parameters')

                input_user = doc.createElement('user')
                input_user.appendChild(doc.createTextNode(self.input.user))

                input_password = doc.createElement('password')
                input_password.appendChild(
                                    doc.createTextNode(self.input.password))

                input_parameters.appendChild(input_user)
                input_parameters.appendChild(input_password)
                input.appendChild(input_parameters)

            file_locations.appendChild(input)

        #output node
        if self.output:
            output = doc.createElement('output')
            output_url = doc.createElement('url')
            output_url.appendChild(doc.createTextNode(self.output.url))
            output.appendChild(output_url)

            if self.output.user and self.output.password:
                output_parameters = doc.createElement('parameters')

                output_user = doc.createElement('user')
                output_user.appendChild(doc.createTextNode(self.output.user))

                output_password = doc.createElement('password')
                output_password.appendChild(
                                    doc.createTextNode(self.output.password))

                output_parameters.appendChild(output_user)
                output_parameters.appendChild(output_password)
                output.appendChild(output_parameters)

            file_locations.appendChild(output)

        #watermark node
        if self.watermark:
            watermark = doc.createElement('watermark')
            watermark_url = doc.createElement('url')
            watermark_url.appendChild(doc.createTextNode(self.watermark.url))
            watermark.appendChild(watermark_url)
            if self.watermark.user and self.watermark.password:
                watermark_parameters = doc.createElement('parameters')

                watermark_user = doc.createElement('user')
                watermark_user.appendChild(
                                    doc.createTextNode(self.watermark.user))

                watermark_password = doc.createElement('password')
                watermark_password.appendChild(
                                    doc.createTextNode(self.watermark.password))

                watermark_parameters.appendChild(watermark_user)
                watermark_parameters.appendChild(watermark_password)
                watermark.appendChild(watermark_parameters)

            file_locations.appendChild(watermark)

        api_req.appendChild(file_locations)

        return doc.toprettyxml(encoding='UTF-8', indent='    ')

    def send(self):
        """Send FlixCloud job request."""
        self.success = False
        if not self.validate():
            print self.errors
            return False

        self.final_xml = self.get_job_xml()

        #HTTPS connection
        headers = {'Accept' : 'text/xml', 'Content-type' : 'application/xml'}
        conn = httplib.HTTPSConnection(host=self.api_base_url)

        #Send job request
        try:
            conn.request('POST', self.api_req_url, self.final_xml, headers)
        except Exception, e:
            self.errors.append('Connection error: %' % e.__str__())
            return False
        response = conn.getresponse()

        self.result['code'] = response.status
        self.result['reason'] = response.reason
        self.result['data'] = response.read()
        self.result['xml'] = xml.dom.minidom.parseString(self.result['data'])

        if response.status == 201:    #Success
            self.success = True
            self.set_job_data()
            return True
        else:                           #Failure
            self.errors.append('Send error: %s, %s' %
                    (self.result['code'],
                    self.result['reason'])
            )
            for error in self.result['xml'].getElementsByTagName('error'):
                self.errors.append(error.firstChild.data)
            return False

    def set_job_data(self):
        """Sets job's data if job was succesfully registered."""
        self.id = xml_int(self.result['xml'], 'id')
        self.initialized_job_at = xml_str(self.result['xml'], 
                                                    'initialized-job-at')

class JobFile:
    """Base class for files (input, output, watermark objects)."""
    def __init__(self, url, user=None, password=None):
        self.name = 'Base'
        self.url = url
        self.user = user
        self.password = password
        self.errors = []

        #From notification:
        self.width = None
        self.height = None
        self.size = None
        self.duration = None
        self.cost = None

    def valid(self):
        """Checks if file object is valid for use."""
        if not self.url:
            self.errors.append('%s: Url is required.' % self.name)
        if (self.user and not self.password) \
                or (self.password and not self.user):
            self.errors.append('%s: Both user & password are required.' %
                                                            self.name)
        if self.errors == []:
            return True
        else:
            return False

class JobInputFile(JobFile):
    """Input file data."""
    def __init__(self, *args, **kwargs):
        JobFile.__init__(self, *args, **kwargs)
        self.name = 'Input'

class JobOutputFile(JobFile):
    """Output file data."""
    def __init__(self, *args, **kwargs):
        JobFile.__init__(self, *args, **kwargs)
        self.name = 'Output'

class JobWatermarkFile(JobFile):
    """Watermark file data."""
    def __init__(self, *args, **kwargs):
        JobFile.__init__(self, *args, **kwargs)
        self.name = 'Watermark'


class JobNotification:
    """Notification about registered job."""
    def __init__(self, msg):
        #job
        self.id = None
        self.finished_job_at = None
        self.initialized_job_at = None
        self.recipe_id = None
        self.recipe_name = None
        self.state = None
        self.error_message = None

        #files
        self.input_media_file = None
        self.output_media_file = None
        self.watermark = None

        self.xml_msg = msg
        self.parse_msg()
        
    def parse_msg(self):
        """Parses xml notification and sets parameters."""
        doc = xml.dom.minidom.parseString(self.xml_msg)
        self.id = xml_int(doc, 'id')
        self.initialized_job_at = xml_str(doc, 'initialized-job-at')
        self.finished_job_at = xml_str(doc, 'finished-job-at')
        self.recipe_id = xml_int(doc, 'recipe-id')
        self.recipe_name = xml_str(doc, 'recipe-name')
        self.state = xml_str(doc, 'state')
        self.error_message = xml_str(doc, 'error-message')

        #files data
        try:
            input_xml = doc.getElementsByTagName('input-media-file')[0]
            self.input_media_file = JobInputFile(xml_str(input_xml, 'url'))
            self.set_file_params(self.input_media_file, input_xml)
        except IndexError:
            print 'No input file defined.'
        try:
            output_xml = doc.getElementsByTagName('output-media-file')[0]
            self.output_media_file = JobOutputFile(xml_str(output_xml, 'url'))
            self.set_file_params(self.output_media_file, output_xml)
        except IndexError:
            print 'No output file defined.'
        try:
            watermark_xml = doc.getElementsByTagName('watermark-file')[0]
            self.watermark_file = JobWatermarkFile(
                                        xml_str(watermark_xml, 'url'))
            self.set_file_params(self.watermark_file, watermark_xml)
        except IndexError:
            print 'No watermark file defined.'

    def set_file_params(self, file, xml_doc):
        """Sets parameters for file according to received notification."""
        file.width = xml_int(xml_doc, 'width')
        file.height = xml_int(xml_doc, 'height')
        file.size = xml_int(xml_doc, 'size')
        file.duration = xml_int(xml_doc, 'duration')
        file.cost = xml_int(xml_doc, 'cost')

    def state(self):
        """Returns jobs state according to received notification."""
        return self.state 

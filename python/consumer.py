# Instructions -- see README.md in this directory
import argparse
import re
import urllib3
import lti
import requests

# see: https://urllib3.readthedocs.io/en/latest/advanced-usage.html#ssl-warnings
urllib3.disable_warnings()


def consume(args):
    launch_params = {
        'context_id': args.context_id,
        'context_title': 'A test class',
        'lis_person_contact_email_primary': args.email,
        'lis_person_name_family': args.last,
        'lis_person_name_given': args.first,
        'resource_link_id': args.resource_link_id,
        'resource_link_title': 'A test assignment',
        'roles': args.role,
        'tool_consumer_info_product_family_code': 'ra-test',
        'tool_consumer_info_version': '0.01',
        'tool_consumer_instance_description': 'RA test consumer',
        'tool_consumer_instance_guid': 'www.revisionassistant.com',
        'user_id': args.user_id,
    }

    if args.ext_grader_id:
        launch_params['ext_grader_id'] = args.ext_grader_id

    if args.env == 'staging':
        launch_url = 'https://staging.tiiscoringengine.com/lti/1p0/launch'
    elif args.env == 'production':
        launch_url = 'https://api.tiiscoringengine.com/lti/1p0/launch'
    else:
        launch_url = 'https://{}.getlightbox.com/lti/1p0/launch'.format(args.env)

    tool_consumer = lti.ToolConsumer(
        args.key, args.secret, params=launch_params, launch_url=launch_url)
    launch_request = tool_consumer.generate_launch_request()
    response = requests.post(
        launch_request.url,
        headers=launch_request.headers, data=launch_request.body,
        allow_redirects=False, verify=False)
    print("Status: {}".format(response.status_code))
    if 'entered a valid consumer key and secret' in response.text:
        print("FAIL: Invalid consumer key/secret")
    elif response.status_code == 302:
        for header in sorted(response.headers):
            print("  {}: {}".format(header, response.headers[header]))
        if 'Location' in response.headers:
            print(response.headers['Location'])
        else:
            pat = re.compile('href="([^"]+)"')
            matches = pat.search(response.text)
            if matches:
                print(matches.group(1))
            else:
                print("Failed to find link in body\n{}".format(response.text))
    else:
        # RA will generate an HTML page with a link in it; we'll pull that link out
        # and display it so you can copy-and-paste
        pat = re.compile('action="([^"]+)"')
        matches = pat.search(response.text)
        if matches:
            print(matches.group(1))
        else:
            print("Failed to find link in response text! Status: {}\n{}".format(response.status_code, response.text))


if __name__ == '__main__':
    parser = argparse.ArgumentParser()

    # env
    parser.add_argument('--env', default='production', help='''
        Revision Assistant environment to launch against, "staging" or "production" (default)
    ''')

    # auth
    parser.add_argument('--key', required=True, help='''
        Consumer auth key, provided by Revision Assistant team (case-sensitive!)
    ''')
    parser.add_argument('--secret', required=True, help='''
        Consumer auth secret, provided by Revision Assistant team (case-sensitive!)
    ''')

    # launch
    parser.add_argument('--context_id', required=True, help='''
        Context (class) identifier, arbitrary and defined by you (required)
    ''')
    parser.add_argument('--email', help='''
        Launching user's email, blank if not provided (blank ok)
    ''')
    parser.add_argument('--ext-grader_id', help='''
        Prompt to launch into with slug provided by Revision Assistant team (don't
        use this unless you know what you're doing)
    ''')
    parser.add_argument('--first', required=True, help='''
        Launching user's first name (required)
    ''')
    parser.add_argument('--last', required=True, help='''
        Launching user's last name (required)
    ''')
    parser.add_argument('--resource_link_id', required=True, help='''
        Resource link (assignment) identifier, arbitrary and defined by you (required)
    ''')
    parser.add_argument('--role', default='Instructor', help='''
        Role, either "Learner" or "Instructor" (default)
    ''')
    parser.add_argument('--user_id', required=True, help='''
        Launching user's external identifier, arbitrary and defined by you (required)
    ''')
    args = parser.parse_args()

    consume(args)

"""
Command-line interface to the stash client functions.
"""
import logging
import os
from ConfigParser import SafeConfigParser

from . import rest
from .rest import UserError, ResponseError


def get_cmd_arguments():
    from argparse import ArgumentParser
    parser = ArgumentParser()
    parser.add_argument("-o", "--organization", action="store", dest="org",
                        help=("Github organization or Stash project to query for repositories to clone."
                              "  Either this or -u is required."))
    parser.add_argument("-u", "--user", action="store", dest="user",
                        help="User to query for repositories to clone.  Either this or -o is required.")
    parser.add_argument("-U", "--override_user", action="store", dest="user_override",
                        help=("Override the local user for accessing stash.  "
                              "If not specified, local user will be used."))
    parser.add_argument("-C", "--create", action="store_true", dest="create",
                        help="Create a repository.")
    parser.add_argument("-perm", "--list_user_permissions", action="store_true", dest="list_user_permissions",
                        help="List the permissions for the users of this project")
    parser.add_argument("-D", action="store_true", dest="delete",
                        help="Delete a repository.")
    parser.add_argument("-v", "--verbose", action="store_true", dest="verbose", help="Log INFO to STDOUT")
    parser.add_argument("-r", "--repo_name", action="store", dest="repo_name",
                        help="The name of the repository.")
    return parser.parse_args()


def main():
    from .models import StashRepo
    logging.basicConfig()
    args = get_cmd_arguments()

    if args.verbose:
        logging.getLogger().setLevel(logging.DEBUG)
    # silly approach that avoids hard-coding the stash repo
    config = SafeConfigParser()
    config.read(os.path.join(os.environ["HOME"], ".stashclientcfg"))
    rest.set_host(config.get('server', 'hostname'))

    if args.delete:
        rest.set_creds(args)
        resp = rest.delete_repo(args.repo_name, user=args.user, project=args.org)
        if resp.text:
            print "Deletion OK: %s" % resp.json().get('message')
        else:
            print "Deletion attempt succeeded with status %d: %s" % (resp.status_code, resp.reason)
    elif args.create:
        rest.set_creds(args)
        resp = rest.create_repo(args.repo_name, user=args.user, project=args.org)
        repo = StashRepo(resp.json())
        print "Successfully created repo %s with clone URL %s" % (repo.name, repo.get_clone_url('ssh'))
    elif args.list_user_permissions:
        rest.set_creds(args)
        rest.list_user_permissions(project=args.org)
    else:
        print "No operation specified."


if '__main__' == __name__:
    try:
        main()
    except KeyboardInterrupt:
        pass
    except UserError as oops:
        print "Input error: %s" % str(oops)
    except ResponseError as fail:
        print "Response unhappy: %s" % str(fail)

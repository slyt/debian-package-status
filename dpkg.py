# This module helps store and organize data taken from the dpkg/status file.
# It provides a Dpkg object that who's state is shared between all instantiations.

import fileparser
import htmlbuilder

# TODO: Specify status file location when running from command line

# Dpkg is a singleton object that allows access to pre-parsed data from the dpkg package manager
# Pre-parsing the dpkg/status file when the server starts instead of on
# each HTTP GET request improves performance.
# The server only serves one dpkg/status file at a time, so the state of Dpkg should be shared
# between all modules and only initialized once.
class Dpkg:

    __instance = None # Keep track if Dpkg has been initialized already

    def __init__(self, filepath='status.real'):
        if Dpkg.__instance != None:
            raise Exception("Can only initialize once (Dpkg is a singleton).")
        else:
            Dpkg.__instance = self
            Dpkg.filepath = filepath # filepath to the /var/lib/dpkg/status file
            packages_raw = fileparser.control_file_to_list(Dpkg.filepath)
            packages = fileparser.clean_packages(packages_raw)  # remove unused fields and add reverse-dependency fields
            Dpkg.packages = sorted(packages, key=lambda k: k['Name'])  # sort packages alphabetically
            Dpkg.package_names = Dpkg.get_package_names()

            # Create a set that we can reference so we don't have to iterate over the
            # list of dictionaries to find if a package exists.
            Dpkg.package_names_set = set(Dpkg.package_names)

            # Convert list of package names to HTML list to use on website homepage
            packages_list_HTML = htmlbuilder.list_to_html_list(Dpkg.package_names, add_hyperlink=True)
            Dpkg.index_html = htmlbuilder.build_html_page(title='Debian Packages',
                                                     body=packages_list_HTML,
                                                     h1='Debian Packages (/var/lib/dpkg/status)')


    @classmethod
    def change_filepath(cls, filepath):
        cls.filepath = filepath  # filepath to the /var/lib/dpkg/status file
        packages_raw = fileparser.control_file_to_list(cls.filepath)
        packages = fileparser.clean_packages(packages_raw)  # remove unused fields and add reverse-dependency fields
        cls.packages = sorted(packages, key=lambda k: k['Name'])  # sort packages alphabetically
        cls.package_names = fileparser.get_package_names(packages)

        # Create a set that we can reference so we don't have to iterate over the
        # list of dictionaries to find if a package exists.
        cls.package_names_set = set(cls.package_names)

        # Convert list of package names to HTML list to use on website homepage
        packages_list_HTML = htmlbuilder.list_to_html_list(cls.package_names, add_hyperlink=True)
        cls.index_html = htmlbuilder.build_html_page(title='Debian Packages',
                                                      body=packages_list_HTML,
                                                      h1='Debian Packages (/var/lib/dpkg/status)')

    @classmethod
    # Finds the first package in a list of packages with the given name and returns it
    def find_package(cls, name):
        for dic in cls.packages:
            if dic.get('Name') == name:
                return dic


    @classmethod
    # Returns a list of package names from a given dictionary
    def get_package_names(cls):
        package_names = []

        for dic in cls.packages:
            package_name = dic.get('Name', '')
            package_names.append(package_name)

        return package_names

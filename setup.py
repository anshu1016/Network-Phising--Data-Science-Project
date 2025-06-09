'''
The setup.py file is an essential part of the packaging and distribution Python projects.
It is used by an setup tools (or distutils in older python versions) to define the configuration of your projects, 
such as its metadata, dependencies and more.
'''


from setuptools import find_packages,setup
from typing import List

requirement_list: List[str] = []
def get_requirements() -> List[str]:
    '''
    This function will return list of requirements.
    '''
    try:
        with open('requirements.txt','r') as file:
            # read lines from the file
            lines = file.readlines()
            # Process each line
            for line in lines:
                requirement = line.strip()
                # ignore empty lines and - e.
                if requirement and requirement != '-e .':
                    requirement_list.append(requirement)

    except FileNotFoundError:
        print('My requirements.txt file not found')


    return requirement_list 


print(get_requirements())
    

setup(
    name = 'NetworkSecurity',
    version='0.0.1',
    author = 'Arun Shukla',
    author_email = 'arunshukla98710@gmail.com',
    packages  = find_packages(),
    install_requires = get_requirements()
)
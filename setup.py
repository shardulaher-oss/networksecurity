from setuptools import setup,find_packages
from typing import List
def get_requirements()->List[str]:
    """
    This Function will return list of requirement
    """
    requirement_lst:List[str]=[]
    try:
        with open("requirement.txt",'r') as file:
            #read lines from files
            lines=file.readlines()
            #Process each line 
            for line in lines :
                requirement=line.strip()
                #ignore emoty lines and -e .
                if requirement and requirement !="-e .":
                    requirement_lst.append(requirement)

    except FileNotFoundError:
        print("requirement.txt file is not found ")
    
    return requirement_lst

setup(
    name="Network Security",
    version="0.0.1",
    author="Shardul Aher",
    author_email="shardulaher@gmail.com",
    packages=find_packages(),
    install_requires=get_requirements()
)
    

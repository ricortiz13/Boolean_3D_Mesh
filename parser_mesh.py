## @author Ricardo Ortiz
#  @date April 20th, 2019
#
class Parser_Mesh(object):
    def __init__(self,filename):
        self.__file_data = []
        self.read_file(filename)
    def read_file(self, filename='model.stl'):
        file = open(filename, 'r')
        for line in file:
            self.__file_data.append(line)
        file.close()
    def get_raw_data(self):
        return self.__file_data

class STL_Parser(Parser_Mesh):
    def read_file(self,filename):
        #facet
        #space delimited
        for line in file:
            __file_data.append(line)
        file.close()

if __name__=='__main__':
    par = Parser()
    par.read_file()

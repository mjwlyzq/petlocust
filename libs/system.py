from os.path import dirname, abspath, isdir, join


def getPath(*paths):
    """
    :param paths: a,b
    :return: ${homedir}/a/b
    """
    return join(dirname(dirname(abspath(__file__))), *paths)

import os, errno, shutil

class SourceSetup(object):
    @staticmethod
    def run(target_epub_dirs, target_epub_files, source_epub_files):
        # make epub resource directories
        for k,dirname in target_epub_dirs.items():
            try:
                os.makedirs(dirname)
            except OSError as e:
                if e.errno != errno.EEXIST:
                    raise
        # copy epub resource files
        for k, filename in source_epub_files.items():
            shutil.copy(filename, target_epub_files[k])
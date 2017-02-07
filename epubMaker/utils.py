def chapterid2filename(chapterid, booktype='tw'):
    chapterid = int(chapterid)
    if booktype == 'tw':
        filename = 'traditional_chapter_{id:04}.xhtml'.format(id=chapterid)  
    else:
        filename = 'simplified_chapter_{id:04}.xhtml'.format(id=chapterid)
    return filename

def articleid2filename(articleid, booktype='tw'):
    articleid = int(articleid)
    if booktype == 'tw':
        filename = 'traditional_article_{id:04}.xhtml'.format(id=articleid)  
    else:
        filename = 'simplified_article_{id:04}.xhtml'.format(id=articleid)
    return filename
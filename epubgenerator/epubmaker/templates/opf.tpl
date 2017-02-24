<?xml version="1.0" encoding="utf-8" standalone="yes"?>
<package xmlns="http://www.idpf.org/2007/opf" prefix="rendition: http://www.idpf.org/vocab/rendition/#" unique-identifier="book-id" version="3.0" xml:lang="en">
   <metadata xmlns:dc="http://purl.org/dc/elements/1.1/">
      <dc:identifier id="book-id">{bookid}</dc:identifier>
      <dc:title>{title}</dc:title>
      <dc:creator>{author}</dc:creator>
      <dc:publisher>{publisher}</dc:publisher>
      <dc:language>zh-cn</dc:language>
      <meta property="dcterms:modified">{datetime}</meta>
      <meta property="rendition:layout">reflowable</meta>
      <meta property="rendition:orientation">auto</meta>
      <meta property="rendition:spread">auto</meta>
      <meta content="0.7.4" name="Sigil version" />
   </metadata>
   <manifest>
   {items}
   </manifest>
   <spine toc="ncx">
   {itemrefs}
   </spine>
   <guide>
      <reference href="{coverpage}" type="cover" />
   </guide>
</package>
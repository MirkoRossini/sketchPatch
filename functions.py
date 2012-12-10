import logging

def clean_sourcecode(sourcecode):
 sourcecode = sourcecode.replace('&','&amp;')
 sourcecode = sourcecode.replace('<','&lt;')
 sourcecode = sourcecode.replace(' ','&nbsp;')
 sourcecode = sourcecode.replace('\r\n','<br>')
 sourcecode = sourcecode.replace('\n','<br>')
 sourcecode = sourcecode.replace('\r','<br>')
 sourcecode = sourcecode.replace('\t','&nbsp;&nbsp;&nbsp;&nbsp;')
 sourcecode = sourcecode.replace('"','&quot;')
 sourcecode = sourcecode.replace("'", '&#39;')
 return sourcecode

def sourcecode_for_text_area(sourcecode):
  sourcecode = sourcecode.replace('&nbsp;',' ')
  sourcecode = sourcecode.replace('<br>','\r\n')
  sourcecode = sourcecode.replace('<br>','\n')
  sourcecode = sourcecode.replace('<br>','\r')
  sourcecode = sourcecode.replace('&nbsp;&nbsp;&nbsp;&nbsp;','\t')
  sourcecode = sourcecode.rstrip().lstrip()
  return sourcecode


def is_suspicious(title,tags):
  logging.info('checking whether its a spam comment')
  if ((len(title) > 9) and  (len(title) < 20)):
    logging.info('length of title is suspicious')
    if (len(re.findall(" ",title)) == 0):
      logging.info('no spaces')
      if len(re.findall("[A-Z]",title)) > 1:
        logging.info('more than one capital letter')
        if (len(tags) > 9) and  (len(tags) < 20):
          logging.info('tags are of the correct length')
          if len(re.findall(" ",tags)) == 0:
            logging.info('no spaces in the tags')
            if len(re.findall(",",tags)) == 0:
              logging.info('no commas in the tags')
              if len(re.findall("[A-Z]",tags)) > 1:
                logging.info('capital letters in the tags')
                logging.info('this sketch is dodgy')
                return True
  return False



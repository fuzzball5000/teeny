import hashlib,getpass,socket, datetime, os, logging, argparse, ConfigParser, logging.handlers,subprocess
from lxml import etree

switch = argparse.ArgumentParser(description='***Teeny. Refer to README for instructions. --generate to generate hash, --compare to compare***')
switch.add_argument('--generate',dest='feature',action='store_true',required=False)
switch.add_argument('--compare',dest='feature',action='store_false',required=False)
switch.add_argument('--ini',help='Path to .ini file',required=True)
switch.set_defaults(feature=False)
a = switch.parse_args().feature
inipath = switch.parse_args().ini
config = ConfigParser.ConfigParser()
config.read(inipath)
outputdir = str((config.get('DEFAULT','output'))) 
#Theres an easier way to get this output into a string. 
path = config.get('DEFAULT','path').split(',')
include = tuple(config.get('DEFAULT','include').split(','))

def main():
    
    if a:
        generator(socket.gethostname(),getpass.getuser(),path,include)
    elif not a:
        comparitor(path_checksum(path),path)
    else:
        exit()

def dirlister(pathin):
    
    with open(outputdir+'/direrrors.txt','w') as errfile:
        op = subprocess.Popen(['ls','-alrtRL',pathin],stdout=subprocess.PIPE).communicate()[0] 
		#Popen is a backport for 2.6 compatibility
        errfile.write(op)

def path_checksum(inpath): 
    #Produces checksum based on file contents. Doesn't care about attributes. 

    hasher = hashlib.sha1() 
	#We will use push file chunks into a hashlib object, and it will be fun!

    if not hasattr(inpath, '__iter__'):
        raise TypeError('I want something to iterate, not a  %r!' % type(inpath))
    #this does not fit the error reporting model, fix. 

    for f in sorted([os.path.normpath(i) for i in inpath]): 
        #Merkle tree? I'm excited... 
        if os.path.exists(f):
            if os.path.isdir(f):
                os.path.walk(f, update_checksum, hasher) 
                #If its a dir, keep walking down tree
            elif os.path.isfile(f):
                update_checksum(hasher, os.path.dirname(f), os.path.basename(f)) #Push file and path to hashlib
    return hasher.hexdigest()

def update_checksum(hashobj, dirname, filenames): 
    for item in sorted(filenames):
        if item.endswith(include): 
            #checks if we care about files, defined in include.
            filepath = os.path.join(dirname, item) 
            #creates /foo/bar.txt style paths
            if os.path.isfile(filepath):
                fh = open(filepath, 'rb')
                while item:
                    chunk = fh.read(4096) 
                    #chunks the read to conserve memory
                    if not chunk: #break at EOF
                        break
                    hashobj.update(chunk)
                fh.close()
            hashobj.update(filepath)
    return()

def generator(hostin,userin,pathin,chkin):
    
    root = etree.Element(hostin)
    doc = etree.ElementTree(root)
    
    for item in pathin: 
        if os.path.exists(item):
            hashin = (path_checksum([item]))
            now = datetime.datetime.now()
            dtstr = now.strftime('%Y-%m-%d %H:%M:%S') 
            #Want a datetime for each file at the time its hashed
            
            pathtree = etree.SubElement(root, 'path') 
            #Creates XML file
            pathtree.text = item
            csum = etree.SubElement(pathtree, 'hash')
            csum.text = hashin
            dt = etree.SubElement(pathtree,'date_time')
            dt.text = str(dtstr)
            user = etree.SubElement(pathtree, 'user')
            user.text = userin
            try:
                outfile = open(outputdir+'/test.xml', 'w') 
                #Writes XML 
                doc.write(outfile)
                logist('Generated new hash for'+str(item)+str(chkin),'info')
            except IOError:
                logist ('Cannot write to output file','error')
                return
            outfile.close
        else:
            print 'Path not found '+item
    return()
        
def comparitor(genhash,pathin):
   
    try:
        root = etree.parse(outputdir+'/test.xml')
    except IOError:
        logist ('Cannot find XML file','error')
        return
    except etree.XMLSyntaxError:
        logist('XML File is invalid, please check','error')
        return
    
    a = 0
    while a <= len(pathin): 
        #Loops through all paths defined in path, generates a new path/hash tuple for each
        try:
            currpath = pathin[a]
            
            xmlreadlisthash = [i.text for i in root.xpath('//hash')] 
            #Adds hash from XML file to list
            xmlreadlist = [i.text for i in root.xpath('//path')] 
            #Adds path from data read from XML file to list
            pathtupe = (xmlreadlist[a],xmlreadlisthash[a]) 
            #Makes tuple based on position (a) in lists above
            hashtupe = (currpath,path_checksum([currpath]))  
            #Makes tuple based on path and freshly genned hash. 

            if pathtupe == hashtupe: 
                #Compares tuples, if hash is different, error. If path is invalid, error. 
                logist('Hash and path equal'+currpath,'info')
            elif not os.path.isdir(currpath):
                logist('Path on OS is different to path defined in teeny, hash invalid'+currpath,'warning')
            elif pathtupe != hashtupe:
                logist('BAD HASH, check error file at:'+' '+outputdir,'warning')
                dirlister(currpath)              
            a=a+1
        except IndexError:
            #print 'End of paths list reached'
            break
        
def logist(messin,pri):

    loggr = logging.getLogger('Teenylog')
    loggr.setLevel(logging.DEBUG)
    handler = logging.handlers.SysLogHandler(address = '/dev/log')
    formatter = logging.Formatter('%(name)s: [%(levelname)s] teeny_hasher: %(message)s')
    handler.setFormatter(formatter)
    loggr.addHandler(handler)
    
    #TODO clean this up, messy. 
    if pri == 'info':
        loggr.info(messin)
        loggr.removeHandler(handler)
        handler.flush()
        handler.close()
    elif pri == 'warning':
        loggr.warning(messin)
        loggr.removeHandler(handler)
        handler.flush()
        handler.close()
    elif pri == 'error':
        loggr.error(messin)
        loggr.removeHandler(handler)
        handler.flush()
        handler.close()
    else:
        return
        
if __name__ == '__main__':
    main()

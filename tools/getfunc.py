import sys,re
def get(path,name):
    s=open(path).read().split('\n')
    for i,l in enumerate(s):
        if re.match(r'^[A-Za-z].*\b'+re.escape(name)+r'\(',l) and not l.rstrip().endswith(';'):
            j=i; depth=0; started=False; out=[]
            while True:
                out.append(s[j]); depth+=s[j].count('{')-s[j].count('}')
                if '{' in s[j]: started=True
                if started and depth==0: return '\n'.join(out)
                j+=1
    return None
if __name__=='__main__':
    for n in sys.argv[2:]: print(get(sys.argv[1],n)); print()

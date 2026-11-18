#include <mgba/core/core.h>
#include <mgba/core/config.h>
#include <mgba/core/serialize.h>
#include <mgba-util/vfs.h>
#include <png.h>
#include <mgba/gba/interface.h>
#include <mgba/core/log.h>
#include <stdarg.h>
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <fcntl.h>
#include <mgba/internal/arm/arm.h>
static struct mCore* core; static mColor* buf; static unsigned W=240,H=160;
static int keymask(const char* s){int k=0; for(;*s;s++){switch(*s){case 'A':k|=1;break;case 'B':k|=2;break;case 's':k|=4;break;case 'S':k|=8;break;case 'R':k|=16;break;case 'L':k|=32;break;case 'U':k|=64;break;case 'D':k|=128;break;case 'r':k|=256;break;case 'l':k|=512;break;}} return k;}
static void shot(const char* fn){FILE* f=fopen(fn,"wb"); png_structp p=png_create_write_struct(PNG_LIBPNG_VER_STRING,0,0,0); png_infop i=png_create_info_struct(p); png_init_io(p,f);
 png_set_IHDR(p,i,W,H,8,PNG_COLOR_TYPE_RGB,PNG_INTERLACE_NONE,PNG_COMPRESSION_TYPE_DEFAULT,PNG_FILTER_TYPE_DEFAULT); png_write_info(p,i);
 unsigned char row[240*3]; for(unsigned y=0;y<H;y++){for(unsigned x=0;x<W;x++){uint32_t c=buf[y*W+x]; row[x*3]=c&0xFF; row[x*3+1]=(c>>8)&0xFF; row[x*3+2]=(c>>16)&0xFF;} png_write_row(p,row);} png_write_end(p,i); png_destroy_write_struct(&p,&i); fclose(f);}
static void nolog(struct mLogger* l,int c,enum mLogLevel lv,const char* f,va_list a){}
static struct mLogger nl={.log=nolog};
int main(int argc,char**argv){
  mLogSetDefaultLogger(&nl);
  if(argc<3){fprintf(stderr,"usage: gbarun rom script [save]\n");return 1;}
  core=mCoreFind(argv[1]); if(!core) return 2;
  core->init(core); mCoreInitConfig(core,NULL);
  buf=malloc(W*H*sizeof(mColor)); core->setVideoBuffer(core,buf,W);
  mCoreLoadFile(core,argv[1]);
  if(argc>3){ struct VFile* sv=VFileOpen(argv[3],O_CREAT|O_RDWR); core->loadSave(core,sv);} 
  core->reset(core);
  FILE* sc=strcmp(argv[2],"-")?fopen(argv[2],"r"):stdin; char line[512];
  while(fgets(line,sizeof line,sc)){
    char cmd[64]="",a1[256]="",a2[256]=""; sscanf(line,"%63s %255s %255s",cmd,a1,a2);
    if(!strcmp(cmd,"run")){int n=atoi(a1); core->setKeys(core,0); for(int i=0;i<n;i++) core->runFrame(core);}
    else if(!strcmp(cmd,"hold")){int k=keymask(a1),n=atoi(a2); core->setKeys(core,k); for(int i=0;i<n;i++) core->runFrame(core); core->setKeys(core,0);}
    else if(!strcmp(cmd,"tap")){int k=keymask(a1),n=a2[0]?atoi(a2):1; for(int j=0;j<n;j++){core->setKeys(core,k); for(int i=0;i<4;i++) core->runFrame(core); core->setKeys(core,0); for(int i=0;i<12;i++) core->runFrame(core);}}
    else if(!strcmp(cmd,"shot")) shot(a1);
    else if(!strcmp(cmd,"ss")){struct VFile* v=VFileOpen(a1,O_CREAT|O_TRUNC|O_RDWR); mCoreSaveStateNamed(core,v,SAVESTATE_SAVEDATA); v->close(v);}
    else if(!strcmp(cmd,"ls")){struct VFile* v=VFileOpen(a1,O_RDONLY); mCoreLoadStateNamed(core,v,SAVESTATE_SAVEDATA); v->close(v);}
    else if(!strcmp(cmd,"peek")){unsigned ad=strtoul(a1,0,16),n=atoi(a2); printf("%08X:",ad); for(unsigned i=0;i<n;i++) printf(" %02X",core->busRead8(core,ad+i)); printf("\n"); fflush(stdout);}
    else if(!strcmp(cmd,"poke")){unsigned ad=strtoul(a1,0,16),v=strtoul(a2,0,16); core->busWrite8(core,ad,v);}
    else if(!strcmp(cmd,"pokeptr")){char a3[64]="";sscanf(line,"%*s %*s %*s %63s",a3);unsigned p=strtoul(a1,0,16); unsigned base=core->busRead32(core,p); core->busWrite8(core,base+strtoul(a2,0,16),strtoul(a3,0,16));}
    else if(!strcmp(cmd,"orptr")){char a3[64]="";sscanf(line,"%*s %*s %*s %63s",a3);unsigned p=strtoul(a1,0,16); unsigned base=core->busRead32(core,p); unsigned ad=base+strtoul(a2,0,16); core->busWrite8(core,ad,core->busRead8(core,ad)|strtoul(a3,0,16));}
    else if(!strcmp(cmd,"reset")) core->reset(core);
    else if(!strcmp(cmd,"regs")){struct ARMCore* c=core->cpu; printf("REGS:"); for(int i=0;i<16;i++) printf(" %08X",c->gprs[i]); printf("\n"); fflush(stdout);}
    else if(!strcmp(cmd,"pc")){printf("frame %u\n",core->frameCounter(core)); fflush(stdout);}
  }

  return 0;
}

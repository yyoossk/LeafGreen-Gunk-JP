#include "global.h"
#include "gflib.h"
// Japanese FireRed's TextPrinter is 0x20 bytes (no minLetterSpacing/japanese at the end); same offsets otherwise
struct JpTextPrinter
{
    struct TextPrinterTemplate printerTemplate;
    void (*callback)(struct TextPrinterTemplate *, u16);
    u8 subUnion[7];
    u8 active;
    u8 state;
    u8 textSpeed;
    u8 delayCounter;
    u8 scrollDistance;
};
extern struct JpTextPrinter sJpTextPrinters[32];
u16 JpRenderFont(struct JpTextPrinter *textPrinter);

#define OPTIONS_TEXT_SPEED_INSTANT 3

void RunTextPrinters(void)
{
    int i;

    for (i = 0; i < 32; ++i)
    {
        if (sJpTextPrinters[i].active)
        {
            bool32 instant = sJpTextPrinters[i].textSpeed == 0 && gSaveBlock2Ptr->optionsTextSpeed == OPTIONS_TEXT_SPEED_INSTANT;
            bool32 printed = FALSE;
            u16 renderCmd;
            u16 n = 0;

            do
            {
                renderCmd = JpRenderFont(&sJpTextPrinters[i]);
                switch (renderCmd)
                {
                case RENDER_PRINT:
                    if (instant)
                        printed = TRUE;
                    else
                        CopyWindowToVram(sJpTextPrinters[i].printerTemplate.windowId, COPYWIN_GFX);
                case RENDER_UPDATE:
                    if (sJpTextPrinters[i].callback != NULL)
                        sJpTextPrinters[i].callback(&sJpTextPrinters[i].printerTemplate, renderCmd);
                    break;
                case RENDER_FINISH:
                    sJpTextPrinters[i].active = FALSE;
                    break;
                }
            } while (instant && renderCmd == RENDER_PRINT && ++n < 0x400);
            if (printed)
                CopyWindowToVram(sJpTextPrinters[i].printerTemplate.windowId, COPYWIN_GFX);
        }
    }
}

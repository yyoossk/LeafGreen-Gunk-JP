import subprocess,sys
def r(s,st): subprocess.run(['python3','/tmp/jprun.py',s,st],check=True,capture_output=True)
subprocess.run(['/home/claude/tools/mkstates.sh'],capture_output=True)
r('/tmp/scn_mt0.txt','/tmp/jst_room.ss'); r('/tmp/scn_bt1.txt','/tmp/cmpst_pallet_out_jp.ss')
r('/tmp/scn_bt2.txt','/tmp/cmpst_bt_arrive_jp.ss'); r('/tmp/scn_bt3.txt','/tmp/cmpst_bt_lobby_jp.ss')
r('/tmp/scn_bt4.txt','/tmp/cmpst_bt_lobby_jp.ss'); r('/tmp/scn_bt5.txt','/tmp/cmpst_bt_party_jp.ss')
r('/tmp/scn_bt6.txt','/tmp/cmpst_bt_chosen_jp.ss')
print('chain ok')

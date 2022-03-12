
import subprocess, os, zipfile, requests, time




version_url = 'https://github.com/Ariescyn/EldenRing-Save-Manager/releases/latest'
r = requests.get(version_url) # Get redirect url
ver = float(r.url.split('/')[-1].split('v')[1])
update_url = f'https://github.com/Ariescyn/EldenRing-Save-Manager/releases/download/v{str(ver)}/EldenRing-Save-Manager-v{str(ver)}-portable.zip'
update_dir = ".\\data\\updates\\"



def update():
    if os.path.isdir(update_dir) is False:
        subprocess.run("md {}".format(update_dir), shell=True, text=True)

    comm1 = f'curl -L {update_url} > {update_dir}upd.zip'

    subprocess.run(comm1, shell=True, text=True)
    with zipfile.ZipFile(f'{update_dir}\\upd.zip', 'r') as fh:
        fh.extractall(f'{update_dir}\\upd')

    comm2 = "Xcopy {} {} /E /H /C /I /Y".format(f'{update_dir}upd',".\\")
    comm3 = f'del {update_dir}upd.zip'
    comm4 = f'rmdir {update_dir}upd /s /q'
    subprocess.run(comm2, shell=True, text=True)
    subprocess.run(comm3, shell=True, text=True)
    subprocess.run(comm4, shell=True, text=True)

print('--- Self Update ---\n')
inp = input(f'Install Latest Elden Ring Save Manager v{str(ver)}?  (yes/no): ')
if inp.lower() in ['yes', 'y']:
    print(f'\nDownloading From: {update_url}\n')
    update()
    print('Finished')
    time.sleep(5)
else:
    print('Cancelled')
    time.sleep(1)

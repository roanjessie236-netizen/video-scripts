# 样片 v2 素材整理：AI 图去黑边、放大；历史照片做成暖色相片卡
import glob, numpy as np
from PIL import Image, ImageOps, ImageFilter
F = '/data/.agent-service/files/'; SRC = '/data/luxun90/preview/src/'; OUT = '/data/luxun90/preview/src2/'
M = dict(p01_brush='7aac99f5-6c46-4fc8-aef0-9b7c7cd6e4a1', p02_luxun_desk='d79487a5-fad4-4e97-a86f-8cdd09c33bba',
 p03_procession='fc4b2c02-c57b-4d54-8473-6b355baaff0b', p04_mourners='c87b63cd-5823-4bee-9cb4-86475c1026aa',
 p05_coffin='ff67e23e-a920-4bbb-9f9e-bbd222ac9a0b', p06_statue='9d9c3f77-7700-4d86-b8de-aa895eba09b9',
 p07_lane_autumn='5c003cd9-2204-4d6d-91dc-e098ba9923b3', p08_desk_ots='59a84c32-1cf2-40b3-a0b2-c4afbb915610',
 p09_clock='5360cb38-b8a7-4703-8179-e344df9147b1', p10_lane_dawn='0d46451f-664a-4be5-9d07-14b23fc80a8c',
 p11_letter='aaba9b7e-3531-497f-9d9d-a5b29674d3c5',
 c01_aerial='adc58288-d3a4-46cc-89e5-4f313f78562d', c02_boat='d0aaa399-e8fe-4dd3-aa66-f54cf489872e',
 c03_gate='e8063611-797a-4df4-a53c-face291235d5', c04_baby='ee99a85d-ddb1-4707-baae-0fa022a3b816',
 c05_beijing='e7f8f9f8-1956-4697-9168-b9a9ef29cebf', c06_bribe='698825d5-0f8a-4db3-831a-9eade60b5299',
 c07_lock='2e5cdde7-6f01-4747-9e47-2abde4b6cefe', c08_father_ill='429ed405-68b3-4d35-a650-dab614160d11',
 c09_doorway='110bfb99-798b-4c74-b65b-a7eaa6493678', c10_snow_bridge='5f371bf9-73eb-433b-aad6-a88c24059f04',
 c11_rain='c569420d-66c7-4291-80ac-bb515c14ecfb', c12_pawn_facade='1e33a49c-c210-487c-90fa-56dec268e74f',
 c13_pawn_counter='e451f3ea-64de-4541-ab8d-6023e9d60deb', c14_hands='4c275eb0-5064-4548-a7f6-7e68b2464346',
 c15_clerk='a0f2e2bf-a513-400f-8806-de81bb6ba738', c16_coins='df09ca13-43d5-4240-9cf0-f8fa5ed070bd',
 c17_pharmacy='22ea4fd8-c693-4e11-9e2a-a1a6e09853c9', c18_dusk='9b650205-a374-42e6-85dd-24ab8371cedc',
 c19_tears='5f3bbc2d-bf6b-47ed-95a8-fc7a7e027925', c20_reeds='2dfb19b9-fb28-4b30-9b78-49c5f7943246',
 c21_cane='6744b259-8f28-4c17-bf5b-79a53c7f3f1f', c22_crickets='6355a839-f6ec-4465-b4a8-c7ff55615525',
 c23_berries='bb3ef068-1581-4dc3-abf6-53e2eb9bb6f3', c24_bedside='d295168b-2867-42a0-a6c0-2cdd410216d3',
 c25_lamp='59650f0f-be62-4139-92d9-a88d8464ac95', c26_gossip='e17c150d-4b92-45e2-9eaa-25460bf50cc8',
 c27_relatives='a8558574-329a-4a4c-bb5b-dde97073afa5', c28_puddle='23304155-d705-46a4-a362-e2a49c9e3880',
 c29_backlit='4e8d3eb8-1e1a-4ddd-8aa1-a7ef4e9e5f1e', c30_reading='1dd154f1-2995-4876-a3be-c7f60c80cfdc',
 c31_bridge_dawn='b76c980b-1d6c-4309-9c1b-5fa982dabf9c', c32_mother_coins='0caf7b19-4d77-4ba5-8e4e-17deffa84c96',
 c33_hands_coins='26544b34-4ed0-42e0-b9ce-75b0e7d4dbe2', c34_mother_cry='c5a4639a-0de8-431b-b2bd-679eb65af5d7',
 c35_boat_leave='d96563e6-7d03-480f-9b02-1a36984ac065')
for k, fid in M.items():
    im = Image.open(glob.glob(F + fid + '/*')[0]).convert('RGB')
    g = np.asarray(im.convert('L')).astype(float); rows, cols = g.mean(1), g.mean(0); h, w = g.shape
    t, b, l, r = 0, h, 0, w
    while t < h // 4 and rows[t] < 6: t += 1
    while b > h * 3 // 4 and rows[b - 1] < 6: b -= 1
    while l < w // 8 and cols[l] < 6: l += 1
    while r > w * 7 // 8 and cols[r - 1] < 6: r -= 1
    im = im.crop((l + 2, t + 2, r - 2, b - 2))
    im = im.resize((2400, round(im.height * 2400 / im.width)), Image.LANCZOS).filter(ImageFilter.UnsharpMask(2, 40, 2))
    im.save(OUT + k + '.jpg', quality=92); print(k, (l, t, r, b), im.size)
CARDS = dict(qj6081=('qj6081-000.jpg', 'sepia'), hz233=('c_hz233.png', 'sepia'), qj2028=('qj2028-000.jpg', None),
             hz231=('c_hz231.png', 'sepia'), hz4=('c_hz4.png', 'sepia'), hz6=('c_hz6.png', 'sepia'), hz7=('c_hz7.png', 'sepia'),
             hz9=('c_hz9.png', 'sepia'), hz10f=('c_hz10f.png', 'sepia'), hz10m=('c_hz10m.png', 'sepia'), hz11=('c_hz11.png', 'sepia'))
for k, (f, tone) in CARDS.items():
    im = Image.open(SRC + f).convert('RGB')
    if tone:
        gg = ImageOps.autocontrast(im.convert('L'), cutoff=0.5)
        im = ImageOps.colorize(gg, black=(40, 30, 22), white=(247, 238, 218))
    s = 1400 / max(im.size)
    if s < 1: im = im.resize((round(im.width * s), round(im.height * s)), Image.LANCZOS)
    im.save(OUT + 'card_' + k + '.jpg', quality=92); print('card', k, im.size)
# 片名书法：白字黑底 → 透明墨迹
t = ImageOps.autocontrast(Image.open(SRC + 'm02_title.jpg').convert('L'), cutoff=0.3)
t.save(OUT + 'title_mask.png')

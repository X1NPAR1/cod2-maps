// metel.gsc -- "Operatsiya Metel", 8 Ocak 1943 (krasnoye'nin devami).
//
// AKIS (kullanici):
//   1) A -- iki katli karakol. A bitmeden B/C yonu gorunmez duvarla kapali.
//   2) B ve C havan mevzileri: bagimsiz, istenen sirayla; Almanlar oyuncu
//      yaklasinca dogar; havan ekipleri havani kullanir (trainyard kalibi).
//   3) SAVUNMA: ekip iki kattaki pencerelere; oyuncu girince kapi/pencere
//      kapanir; sis + hurra; 50 yaya (6 sn'de 5-7) + kamyon + iki yarim
//      paletli. 6 Alman kalinca canlari 1, dogduklari yere kacip silinir.
//   4) FINAL: kacisla final muzigi (dongu); ekip avluda cember (oyuncuya bir
//      bosluk); herkes yerindeyken oyuncu gelince Leonov konusur; 3 sn sonra
//      7 sn'de kararma, bolum biter.
// Kaliplar krasnoye'de oyunda calismis olanlar + stok: _mortar generic_style
// (bergstein), objective_current(a,b) (hill400), _mortarteam (trainyard),
// script_brushmodel notsolid (crossroads), throwSmoke (demolition).
#include maps\_utility;
#include maps\_anim;

main()
{
	setExpFog(0.00028, .62, .66, .72, 0);
	setCullDist(11000);

	precacheString(&"METEL_OBJ_B");
	precacheString(&"METEL_OBJ_C");
	precacheString(&"METEL_OBJ_A");
	precacheString(&"METEL_OBJ_SAVUN");
	precacheString(&"METEL_OBJ_TOPLAN");
	precacheString(&"METEL_BITTI");
	precacheString(&"METEL_INTRO_TITLE");
	precacheString(&"METEL_INTRO_PLACE");
	precacheString(&"METEL_INTRO_DATE");
	precacheString(&"METEL_INTRO_INFO");
	precacheShader("black");
	precacheItem("smoke_grenade_american");     // demolition throwSmoke

	level.campaign = "russian";
	// friendly_wave sayaci _load'dan ONCE (krasnoye olcusu: _spawner.gsc:2817)
	level.totalfriends = 0;
	level.maxfriendlies = 7;
	maps\_truck::main("xmodel/vehicle_opel_blitz_snow");
	maps\_halftrack::main("xmodel/vehicle_halftrack_mg_snow");
	maps\metel_fx::main();
	maps\_mortar::generic_style_init();
	maps\_load::main();
	maps\metel_anim::main();
	maps\_mortarteam::main();                  // havan ekibi animasyonlari (trainyard)
	level.mortar = level._effect["havan_b"];    // _mortarteam fire() isabet efekti
	setEnvironment("cold");

	level.maxfriendlies = 7;                    // oyuncu + 7 = 8 kisi
	level.friendlyMethod = "friendly chains";
	level.friendlywave_thread = ::yeni_takviye;
	level.ekip_mod = "takip";
	level.followmin = -2;
	level.followmax = 2;

	flag_init("b_temiz");
	flag_init("c_temiz");
	flag_init("a_temiz");
	flag_init("savunma_bitti");
	level.karsi_toplam = 50;
	level.karsi_dogan = 0;

	// acilista takviye yok; oyuncu her zaman bir zincirde (krasnoye olcusu)
	level.dalga_tetik = getentarray("friendly_wave", "targetname");
	for (i = 0; i < level.dalga_tetik.size; i++)
		level.dalga_tetik[i] triggerOff();
	level.player setfriendlychain(getnode("fc_baslangic", "targetname"));

	if (getcvar("kr_tur") != "" && getcvar("kr_tur") != "0")
	{
		level thread ekran_turu();
		return;
	}

	oyuncu_techizat();
	siper_onbellek();
	level thread tanitim();
	ekip_kur();
	// Alman tufek atip Luger cekmesin (animscripts combat_utility
	// tryWeaponThrowDown; bayrak ilk AI init'inde false yapilir -> ekipten sonra)
	anim.noWeaponToss = true;
	engeller_kur();
	level thread grup_dogur("alman_a");
	level thread havan_kur("havan_b");
	level thread havan_kur("havan_c");
	level thread zincir_takip();
	level thread takviye_bildir();
	level thread gorevler();
	if (getcvar("kr_test") == "1")
		level thread otomatik_test();
	if (getcvar("kr_test") == "2")
		level thread dost_olcum();
	if (getcvar("kr_test") == "3")
		level thread tani_olcum();
}

// --------------------------------------------------------------------------
// TANITIM -- stok _introscreen kalibi; siyah perde 3 sn'de acilir
// --------------------------------------------------------------------------
tanitim()
{
	level.introblack = newHudElem();
	level.introblack.x = 0;
	level.introblack.y = 0;
	level.introblack.horzAlign = "fullscreen";
	level.introblack.vertAlign = "fullscreen";
	level.introblack.foreground = true;
	level.introblack setShader("black", 640, 480);
	level.player freezeControls(true);
	musicplay("metel_muzik_giris");
	wait .05;
	level.introstring = [];
	maps\_introscreen::introscreen_create_line(&"METEL_INTRO_TITLE");
	wait 2;
	maps\_introscreen::introscreen_create_line(&"METEL_INTRO_PLACE");
	maps\_introscreen::introscreen_create_line(&"METEL_INTRO_DATE");
	wait 2;
	maps\_introscreen::introscreen_create_line(&"METEL_INTRO_INFO");
	wait 3;
	level.introblack fadeOverTime(3);
	level.introblack.alpha = 0;
	level.player freezeControls(false);
	maps\_introscreen::introscreen_fadeOutText();
	level notify("tanitim_bitti");
}

// Kullanici: birincil Mosin, ikincil tabanca (TT-30); 4 el bombasi, 4 duman
oyuncu_techizat()
{
	level.player takeallweapons();
	level.player giveWeapon("mosin_nagant");
	level.player giveWeapon("tt30");
	level.player giveWeapon("RGD-33russianfrag");
	level.player giveWeapon("smoke_grenade_russian");
	level.player giveMaxAmmo("mosin_nagant");
	level.player giveMaxAmmo("tt30");
	level.player setWeaponClipAmmo("RGD-33russianfrag", 4);
	level.player setWeaponClipAmmo("smoke_grenade_russian", 4);
	level.player switchToWeapon("mosin_nagant");
	level.player switchToOffhand("RGD-33russianfrag");
	maps\_loadout::setup_russian();
}

// --------------------------------------------------------------------------
// EKIP: Leonov (olumsuz) + 6 asker yikik evin icinde; takviye friendly_wave
// ile harita disindaki guney vadisinden, oyuncu gormeden gelir.
// --------------------------------------------------------------------------
ekip_kur()
{
	sp = getent("leonov", "targetname");
	level.leonov = sp dospawn();
	if (spawn_failed(level.leonov))
		level.leonov = sp stalingradspawn();
	level.leonov.animname = "leonov";
	level.leonov thread magic_bullet_shield();
	level.leonov.dontavoidplayer = true;

	level.ekip = [];
	level.ekip[0] = level.leonov;
	ekip = getentarray("ekip", "targetname");
	for (i = 0; i < ekip.size; i++)
	{
		guy = ekip[i] dospawn();
		if (spawn_failed(guy))
			guy = ekip[i] stalingradspawn();
		if (spawn_failed(guy))
			continue;
		level.ekip[level.ekip.size] = guy;
	}
	// tanitim boyunca yikik evin icinde yerlerinde beklerler
	for (i = 0; i < level.ekip.size; i++)
	{
		level.ekip[i].goalradius = 32;
		level.ekip[i] setgoalpos(level.ekip[i].origin);
	}
}

friendlyMethod(guy)
{
	if (!isdefined(guy))
		guy = self;
	guy.followmin = level.followmin;
	guy.followmax = level.followmax;
	guy.friendlyWaypoint = false;
	guy.goalradius = 320;
	guy setgoalentity(level.player);
}

// Ekip modu (kullanici): "takip" -> oyuncuyu izle; "hucum" -> B/C'de
// Almanlar dogunca oraya saldir; "pencere" -> karakolun pencerelerine.
yeni_takviye(guy)
{
	if (level.ekip_mod == "hucum")
	{
		guy.goalradius = 500;
		guy setgoalpos(level.hucum_merkez);
	}
	else if (level.ekip_mod == "takip")
		friendlyMethod(guy);
	// "pencere": pencere_bekcisi yerlestirir
}

ekip_takibe()
{
	level.ekip_mod = "takip";
	ai = getaiarray("allies");
	for (i = 0; i < ai.size; i++)
		friendlyMethod(ai[i]);
}

// B/C'de Almanlar dogunca ekip takibi birakir, mevziye hucum eder;
// mevzi temizlenince yeniden takibe gecer.
ekip_hucum(merkez, bayrak)
{
	level notify("yeni_hucum");
	level endon("yeni_hucum");
	level.ekip_mod = "hucum";
	level.hucum_merkez = merkez;
	while (!flag(bayrak))
	{
		ai = getaiarray("allies");
		for (i = 0; i < ai.size; i++)
		{
			ai[i].goalradius = 500;
			ai[i] setgoalpos(merkez);
		}
		wait 4;
	}
	if (level.ekip_mod == "hucum")
		ekip_takibe();
}

ekip_harekete()
{
	for (i = 0; i < level.ekip.size; i++)
		if (isalive(level.ekip[i]))
			friendlyMethod(level.ekip[i]);
	for (i = 0; i < level.dalga_tetik.size; i++)
		level.dalga_tetik[i] triggerOn();
	level notify("ekip_yola_cikti");
}

// Oyuncu hangi bolgedeyse ekip o bolgenin zincirini kullanir (stok
// trigger_friendlychain ile ayni is). Savunmada durur.
zincir_takip()
{
	level endon("savunma_basladi");
	level waittill("ekip_yola_cikti");
	ad = [];
	ad[ad.size] = "fc_baslangic";	ad[ad.size] = "fc_guney";	ad[ad.size] = "fc_kavsak";
	ad[ad.size] = "fc_bati";		ad[ad.size] = "fc_brampa";	ad[ad.size] = "fc_b";
	ad[ad.size] = "fc_dogu";		ad[ad.size] = "fc_dogu2";	ad[ad.size] = "fc_cpatika";
	ad[ad.size] = "fc_c";			ad[ad.size] = "fc_kuzey";	ad[ad.size] = "fc_kuzeydogu";
	ad[ad.size] = "fc_avlu";
	bas = [];
	for (i = 0; i < ad.size; i++)
		bas[i] = getnode(ad[i], "targetname");
	zemin = getnode("fc_zemin", "targetname");
	ust = getnode("fc_ust", "targetname");
	simdiki = undefined;
	for (;;)
	{
		wait 1;
		p = level.player.origin;
		secim = undefined;
		if (oyuncu_binada())
		{
			if (p[2] > 200)
				secim = ust;
			else
				secim = zemin;
		}
		else
		{
			en = 999999;
			for (i = 0; i < bas.size; i++)
			{
				d = distance(p, bas[i].origin);
				if (d < en)
				{
					en = d;
					secim = bas[i];
				}
			}
		}
		if (!isdefined(simdiki) || simdiki != secim)
		{
			simdiki = secim;
			level.player setfriendlychain(secim);
		}
	}
}

oyuncu_binada()
{
	p = level.player.origin;
	return (p[0] > -710 && p[0] < 410 && p[1] > 134 && p[1] < 806);
}

// takviye dogdugunda arada bir (4 dk'da en fazla bir) bir asker haber verir
takviye_bildir()
{
	son = 0;
	for (;;)
	{
		level waittill("friendly_died");
		if (gettime() - son < 240000)
			continue;
		wait 6;
		son = gettime();
		ai = getaiarray("allies");
		for (i = 0; i < ai.size; i++)
		{
			if (isdefined(level.leonov) && ai[i] == level.leonov)
				continue;
			ai[i].animname = "generic";
			ai[i] thread Dialogue_Thread("takviye");
			break;
		}
	}
}

Dialogue_Thread(dialogue)
{
	self setBattleChatter(false);
	self anim_single_solo(self, dialogue);
	self setBattleChatter(true);
}

leonov_der(replik)
{
	if (!isdefined(level.leonov) || !isalive(level.leonov))
		return;
	g = level.leonov;
	g endon("death");
	if (isdefined(g.MyIsSpeaking) && g.MyIsSpeaking)
		g waittill("my done speaking");
	g.MyIsSpeaking = true;
	g setBattleChatter(false);
	g anim_single_solo(g, replik);
	g setBattleChatter(true);
	g.MyIsSpeaking = false;
	g notify("my done speaking");
}

// parca gecisi: once sondur (stok demolition music_awaitingattack)
muzik(alias)
{
	level notify("muzik_degisti");
	level endon("muzik_degisti");
	musicstop(2);
	wait 2.1;
	musicplay(alias);
}

// --------------------------------------------------------------------------
// ALMANLAR
// --------------------------------------------------------------------------
// Grup dogurma; spawner'lar SILINIR (waittill_aigroupcleared spawner'i da sayar)
grup_dogur(ad)
{
	ekip = [];
	sp = getentarray(ad, "targetname");
	for (i = 0; i < sp.size; i++)
	{
		guy = sp[i] stalingradspawn();
		if (spawn_failed(guy))
			continue;
		if (ad == "alman_a")
		{
			guy thread karakol_savunucu();
			continue;
		}
		merkez = (-2310, 1350, 210);
		yar = 520;
		if (ad == "alman_c")
		{
			merkez = (2730, 1080, 240);
			yar = 620;
		}
		guy.mevzi_merkez = merkez;
		guy.mevzi_yar = yar;
		if (i < 2)
			ekip[ekip.size] = guy;              // ilk ikisi havan ekibi
		else
			guy thread mevzi_savunucu(merkez, yar);
	}
	if (ekip.size == 2)
		level thread havan_ekibi(getsubstr(ad, 6), ekip);
	wait 0.5;
	for (i = 0; i < sp.size; i++)
		if (isdefined(sp[i]))
			sp[i] delete();
}

// kullanici: B ve C'nin Almanlari oyuncu YAKLASINCA dogar (A temizlendikten sonra)
yaklasinca_dogur(ad, merkez, mesafe)
{
	while (distance((level.player.origin[0], level.player.origin[1], 0), merkez) > mesafe)
		wait 0.5;
	grup_dogur(ad);
	if (!flag("b_temiz") || !flag("c_temiz"))
	{
		bayrak = "b_temiz";
		if (ad == "alman_c")
			bayrak = "c_temiz";
		level thread ekip_hucum(merkez + (0, 0, 0), bayrak);
	}
}

// HAVAN EKIBI (kullanici: "almanlar mortari kullansin") -- trainyard.gsc
// MortarCrew_Spawn / Mortar_LoadAndFire birebir: dolduran + nisanci, stok
// _mortarteam animasyonlari (bekle, mermi al, ates). Ekipten biri vurulunca
// ya da yakina bomba dusunce ekip silahina doner; o mevzinin baraji susar.
havan_ekibi(harf, ekip)
{
	havan = getent("havan_" + harf + "_top", "targetname");
	for (i = 0; i < ekip.size; i++)
		ekip[i] thread havanci_bozul(ekip, harf);
	havan.isabet_adi = "havan_" + harf;
	havan thread havan_atesle(ekip);
	level waittill("havan_ekibi_bozuldu_" + harf);
	havan notify("stop");
	level notify("havan_" + harf + "_dur");
}

havanci_bozul(ekip, harf)
{
	level endon("havan_ekibi_bozuldu_" + harf);
	self.ignoreme = true;
	self.ignoreall = true;                      // havan basindayken ates etmez (tag_flash hatasi)
	// kullanici: ekipten biri VURULMADIKCA ikisi de havani birakmaz
	self waittill_any("death", "damage");
	for (i = 0; i < ekip.size; i++)
	{
		g = ekip[i];
		if (!isalive(g))
			continue;
		g.ignoreme = false;
		g.ignoreall = false;
		g animscripts\shared::putGunInHand("right");
		g stopAnimScripted();
		g notify("stopIdle");
		if (isdefined(g.mortarAmmo) && g.mortarAmmo)
		{
			g detach("xmodel/prop_mortar_ammunition", "TAG_WEAPON_RIGHT");
			g.mortarAmmo = false;
		}
		g thread mevzi_savunucu(g.mevzi_merkez, g.mevzi_yar);
	}
	level notify("havan_ekibi_bozuldu_" + harf);
}

havan_atesle(ekip)
{
	self endon("stop");
	ekip[0] endon("death");
	ekip[1] endon("death");
	ekip[0].animname = "loadguy";
	ekip[1].animname = "aimguy";
	ekip[0] animscripts\shared::putGunInHand("none");
	ekip[1] animscripts\shared::putGunInHand("none");
	// stok _mortarteam fire() (atis notetrack'i) bu alanlari ister (trainyard)
	self.mortarEnt = self;
	self.mortar = self;
	self.mortar_targets = getentarray(self.isabet_adi, "targetname");
	self anim_single_solo(ekip[1], "fire");
	for (;;)
	{
		self thread anim_loop(ekip, "wait_idle", undefined, "stopIdle");
		wait randomFloatRange(4.0, 6.0);
		self notify("stopIdle");
		self anim_single(ekip, "pickup");
		self anim_single(ekip, "fire");          // ses, alev ve mermi stok fire() ile
	}
}

siper_onbellek()
{
	level.siper = [];
	level.bina_ic = [];
	nodes = getallnodes();
	for (i = 0; i < nodes.size; i++)
	{
		if (issubstr(nodes[i].type, "Cover"))
			level.siper[level.siper.size] = nodes[i];
		o = nodes[i].origin;
		if (o[0] > -700 && o[0] < 400 && o[1] > 150 && o[1] < 790)
			level.bina_ic[level.bina_ic.size] = nodes[i];
	}
}

hedef_bekle(sure)
{
	self endon("goal");
	wait sure;
}

// MEVZI SAVUNUCUSU: mevzideki siperler arasinda yer degistirir, oyuncu
// yaklasinca geri cekilip baska sipere gecer (krasnoye koy_savunucu kalibi)
mevzi_savunucu(merkez, yaricap)
{
	self endon("death");
	self bolge_dolas(merkez, yaricap, -9999, 9999);
}

// KARAKOL SAVUNUCUSU: dogdugu katta/avluda kalir, o bolgede siper degistirir
karakol_savunucu()
{
	self endon("death");
	z = self.origin[2];
	if (z > 200)
		self bolge_dolas((-150, 470, 232), 700, 200, 9999);
	else if (self.origin[0] > -726 && self.origin[0] < 426 && self.origin[1] > 118 && self.origin[1] < 822)
		self bolge_dolas((-150, 470, 24), 700, 0, 200);
	else
		self bolge_dolas((-150, 200, 0), 950, -9999, 120);
}

bolge_dolas(merkez, yaricap, zmin, zmax)
{
	self endon("death");
	self endon("kaciyor");
	wait randomfloatrange(2, 6);
	for (;;)
	{
		p = level.player.origin;
		yakin = distance(self.origin, p) < 550;
		aday = [];
		for (i = 0; i < level.siper.size; i++)
		{
			n = level.siper[i];
			if (n.origin[2] < zmin || n.origin[2] > zmax)
				continue;
			if (distance((n.origin[0], n.origin[1], 0), (merkez[0], merkez[1], 0)) > yaricap)
				continue;
			dn = distance(n.origin, self.origin);
			if (dn < 100 || dn > 700)
				continue;
			if (distance(n.origin, p) < 300)
				continue;
			if (yakin && distance(n.origin, p) < distance(self.origin, p))
				continue;
			aday[aday.size] = n;
		}
		if (aday.size)
		{
			self.goalradius = 80;
			self setgoalnode(aday[randomint(aday.size)]);
			self hedef_bekle(10);
		}
		if (yakin)
			wait randomfloatrange(2, 4);
		else
			wait randomfloatrange(8, 16);
	}
}

// --------------------------------------------------------------------------
// GORUNMEZ DUVARLAR: B/C engeli acik; savunma kapi/pencere engelleri pasif
// --------------------------------------------------------------------------
// Engeller derlemede 2000 birim yukarida (gokyuzunde) durur: AI yol agi
// engelsiz hesaplanir (olculdu: derlemedeki clip_player kapilari ve sinir
// gecitlerini yol aginda da kapatiyordu). Burada yerlerine indirilir.
engeller_kur()
{
	level.engel_bc = getent("engel_bc", "targetname");
	level.engel_bc engel_indir();
	level.savunma_duvar = getent("savunma_duvar", "targetname");
	level.sinir = maps\metel_sinir::cokgen();
	level thread sinir_bekcisi();
}

// OYUNCU SINIRI: clip_player AI'yi de fiziksel durdurdugu icin (olculdu:
// takviyeler ve vadilerden gelen Almanlar sinir gecidinde takiliyordu)
// gecitler ACIK; oyuncu cokgen disina cikarsa son gecerli yerine alinir.
sinir_bekcisi()
{
	son = level.player.origin;
	for (;;)
	{
		p = level.player.origin;
		if (cokgen_icinde(p, level.sinir))
			son = p;
		else
			level.player setorigin(son);
		wait 0.05;
	}
}

cokgen_icinde(p, poli)
{
	ic = false;
	n = poli.size;
	for (i = 0; i < n; i++)
	{
		a = poli[i];
		b = poli[(i + 1) % n];
		if ((a[1] > p[1]) != (b[1] > p[1]))
		{
			x = (b[0] - a[0]) * (p[1] - a[1]) / (b[1] - a[1]) + a[0];
			if (p[0] < x)
				ic = !ic;
		}
	}
	return ic;
}

// SAVUNMA: kapi ve pencerelere yalniz oyuncuyu durduran duvar (clip_player)
// iner -- ekip iceri girdikten sonra (en fazla 25 sn beklenir). Yol agi bu
// duvar yokken hesaplandi; kacis baslayinca duvar kalkar.
savunma_duvari()
{
	for (t = 0; t < 25; t++)
	{
		if (oyuncu_binada() && ekip_icerde() >= getaiarray("allies").size - 1)
			break;
		wait 1;
	}
	while (!oyuncu_binada())
		wait 0.25;
	level.savunma_duvar engel_indir();
	level waittill("almanlar_kaciyor");
	level.savunma_duvar moveZ(2000, 0.05);
}

ekip_icerde()
{
	n = 0;
	ai = getaiarray("allies");
	for (i = 0; i < ai.size; i++)
	{
		o = ai[i].origin;
		if (o[0] > -710 && o[0] < 410 && o[1] > 134 && o[1] < 806)
			n++;
	}
	return n;
}

// (eski betik bekcisi -- artik kullanilmiyor)
bina_bekcisi()
{
	level endon("almanlar_kaciyor");
	son = level.player.origin;
	for (;;)
	{
		if (oyuncu_binada())
			son = level.player.origin;
		else
			level.player setorigin(son);
		wait 0.05;
	}
}

engel_indir()
{
	self moveZ(-2000, 0.05);
}

// --------------------------------------------------------------------------
// HAVAN BARAJI: stok generic_style; isabet noktalari oyuncu yolu boyunca.
// Mevzi temizlenince ya da ekip saldiriya ugrayinca durur.
// --------------------------------------------------------------------------
havan_kur(ad)
{
	level.explosion_startNotify[ad] = "havan_basla";
	level.explosion_stopNotify[ad] = ad + "_dur";
	level thread maps\_mortar::generic_style(ad, 5, undefined, undefined, 500, 2400, undefined);
	namlu = getent(ad + "_namlu", "targetname");
	level endon(ad + "_dur");
	for (;;)
	{
		level waittill("explosion", hangi);
		if (hangi == ad)
			playfx(level._effect["havan_namlu"], namlu.origin);
	}
}

// baraj, oyuncu baslangictan ilerleyince baslar (ilk anda catisma olmasin)
havan_baslat()
{
	while (level.player.origin[1] < -1700)
		wait 0.5;
	level notify("havan_basla");
}

// --------------------------------------------------------------------------
// GOREV AKISI
// --------------------------------------------------------------------------
gorevler()
{
	level waittill("tanitim_bitti");
	level thread muzik("metel_muzik_yaklasma");
	wait 1;
	leonov_der("giris");
	ekip_harekete();
	// 1) A -- karakol (A bitmeden B/C'ye gidilemez)
	objective_add(1, "active", &"METEL_OBJ_A", (-150, 470, 0));
	objective_current(1);
	level thread havan_baslat();
	level thread kapi_konusmasi();
	level thread ust_kat_takip();
	level thread leonov_der("karakol");
	waittill_aigroupcleared("karakol");
	flag_set("a_temiz");
	objective_state(1, "done");
	autoSaveByName("karakol");
	level.engel_bc delete();
	level thread muzik("metel_muzik_catisma");
	level thread leonov_der("hucum");

	// 2) B ve C -- bagimsiz, istenen sirayla; askerler yaklasinca dogar
	objective_add(2, "active", &"METEL_OBJ_B", (-2370, 1390, 210));
	objective_add(3, "active", &"METEL_OBJ_C", (2710, 1140, 240));
	objective_current(2, 3);
	level thread yaklasinca_dogur("alman_b", (-2310, 1350, 0), 1900);
	level thread yaklasinca_dogur("alman_c", (2730, 1080, 0), 1900);
	level thread mevzi_bekle("mevzi_b", "b_temiz", 2, "havan_b_dur");
	level thread mevzi_bekle("mevzi_c", "c_temiz", 3, "havan_c_dur");
	flag_wait("b_temiz");
	flag_wait("c_temiz");

	// 3) SAVUNMA
	wait 2;
	level thread muzik("metel_muzik_savunma");
	objective_add(4, "active", &"METEL_OBJ_SAVUN", (-150, 470, 0));
	objective_current(4);
	ekip_pencerelere();
	leonov_der("savunma");
	while (!oyuncu_binada())
		wait 0.5;
	level thread savunma_duvari();              // oyuncu binadan cikamaz (gercek duvar)
	wait 8;
	sis_patlat();                               // saldiridan hemen once sis
	wait 2;
	hurra();
	level thread leonov_der("saldiri");
	level thread karsi_saldiri();
	level thread arac_dalgasi();
	// 50 yaya dogdu, araclar geldi, 6 Alman kaldi -> canlari 1, kacarlar
	while (level.karsi_dogan < level.karsi_toplam || !isdefined(level.araclar_tamam) || getaiarray("axis").size > 6)
		wait 0.5;
	level notify("almanlar_kaciyor");
	ai = getaiarray("axis");
	for (i = 0; i < ai.size; i++)
		ai[i] thread alman_kac();
	flag_set("savunma_bitti");
	objective_state(4, "done");
	autoSaveByName("savunma");
	level thread muzik("metel_muzik_final");   // final muzigi dongude
	level thread leonov_der("kacis");

	// 4) FINAL: herkes disari, avluda cember; oyuncu icin bir bosluk
	merkez = getent("daire_merkez", "targetname").origin;
	level thread final_cember(merkez);
	objective_add(5, "active", &"METEL_OBJ_TOPLAN", merkez);
	objective_current(5);
	// Leonov ve HAYATTAKI butun askerler yerini almadan konusma yok
	for (;;)
	{
		wait 0.25;
		if (!cember_hazir())
			continue;
		if (isdefined(level.oyuncu_yeri) && distance(level.player.origin, level.oyuncu_yeri) < 110)
			break;
	}
	objective_state(5, "done");
	level notify("oyuncu_cemberde");
	leonov_der("final1");
	leonov_der("final2");
	level thread zafer_atesi();
	iprintlnbold(&"METEL_BITTI");
	wait 3;                                     // konusma bitti + 3 sn
	bolum_sonu();
}

mevzi_bekle(grup, bayrak, obj, dur)
{
	// grup henuz dogmadiysa aigroup tanimsizdir: once dogmasini bekle
	while (!isdefined(level._ai_group) || !isdefined(level._ai_group[grup]))
		wait 1;
	waittill_aigroupcleared(grup);
	level notify(dur);                          // o mevzinin havani susar
	flag_set(bayrak);
	objective_state(obj, "done");
	autoSaveByName(grup);
	if (flag("b_temiz") && flag("c_temiz"))
		level thread leonov_der("havan2");
	else
	{
		level thread leonov_der("havan1");
		if (obj == 2)
			objective_current(3);
		else
			objective_current(2);
	}
}

kapi_konusmasi()
{
	while (distance((level.player.origin[0], level.player.origin[1], 0), (-150, 0, 0)) > 650)
		wait 0.5;
	leonov_der("kapi");
}

// ust kattaki savunucular bitti ve oyuncu yukarida -> "Ust kat temiz!"
ust_kat_takip()
{
	for (;;)
	{
		wait 1;
		if (flag("a_temiz"))
			return;
		if (level.player.origin[2] < 200)
			continue;
		ai = getaiarray("axis");
		kalan = 0;
		for (i = 0; i < ai.size; i++)
			if (ai[i].origin[2] > 200)
				kalan++;
		if (kalan == 0)
		{
			leonov_der("ust_temiz");
			return;
		}
	}
}

// --------------------------------------------------------------------------
// SAVUNMA
// --------------------------------------------------------------------------
// Ekip karakolun iki katindaki PENCERE siperlerine dagilir: zincir takibi
// durur, her askere ayri bir siper (katlar sirayla), sonradan gelen
// takviyeler de bos siperlere yerlesir.
ekip_pencerelere()
{
	level notify("yeni_hucum");                 // varsa hucum biter
	level notify("savunma_basladi");            // zincir takibi durur
	level.ekip_mod = "pencere";
	level.pencere = [];
	alt = [];
	ust = [];
	for (i = 0; i < level.siper.size; i++)
	{
		o = level.siper[i].origin;
		if (!(o[0] > -726 && o[0] < 426 && o[1] > 118 && o[1] < 822))
			continue;
		if (o[2] > 200)
			ust[ust.size] = level.siper[i];
		else
			alt[alt.size] = level.siper[i];
	}
	for (i = 0; i < alt.size || i < ust.size; i++)
	{
		if (i < ust.size)
			level.pencere[level.pencere.size] = ust[i];
		if (i < alt.size)
			level.pencere[level.pencere.size] = alt[i];
	}
	level.pencere_sahip = [];
	level thread pencere_bekcisi();
}

pencere_bekcisi()
{
	level endon("almanlar_kaciyor");
	for (;;)
	{
		ai = getaiarray("allies");
		for (i = 0; i < ai.size; i++)
		{
			g = ai[i];
			if (!isdefined(g.pencere_no))
			{
				no = pencere_bos();
				if (no < 0)
					continue;
				g.pencere_no = no;
				level.pencere_sahip[no] = g;
			}
			n = level.pencere[g.pencere_no];
			if (distance(g.origin, n.origin) > 40)
			{
				g.goalradius = 24;
				g setgoalpos(n.origin);         // konum hedefi (setgoalnode ile kimse kipirdamadi)
			}
		}
		wait 4;
	}
}

pencere_bos()
{
	for (i = 0; i < level.pencere.size; i++)
		if (!isdefined(level.pencere_sahip[i]) || !isalive(level.pencere_sahip[i]))
			return i;
	return -1;
}

// saldiridan hemen once: Almanlarin geldigi yollarda sis (demolition
// smokeGen/throwSmoke kalibi; atici olarak Leonov kullanilir)
sis_patlat()
{
	nok = [];
	nok[nok.size] = (-3000, -470, 0);  nok[nok.size] = (-2460, -550, 0);  nok[nok.size] = (-1740, -600, 0);
	nok[nok.size] = (3060, 150, 0);    nok[nok.size] = (2640, 90, 0);     nok[nok.size] = (2190, 0, 0);
	nok[nok.size] = (-600, -2510, 0);  nok[nok.size] = (-180, -2420, 0);  nok[nok.size] = (60, -1980, 0);
	atan = level.leonov;
	for (i = 0; i < nok.size; i++)
	{
		tr = bulletTrace(nok[i] + (0, 0, 900), nok[i] - (0, 0, 900), false, undefined);
		yer = tr["position"];
		eski = atan.grenadeWeapon;
		atan.grenadeWeapon = "smoke_grenade_american";
		atan.grenadeAmmo++;
		atan MagicGrenade(yer + (0, 0, 40), yer, 0.4);
		atan.grenadeWeapon = eski;
		wait (0.3 + randomfloat(0.4));
	}
}

// demolition exploder 51 "german Walla": saldiri oncesi hurra kalabaligi
hurra()
{
	yerler = [];
	yerler[0] = getentarray("karsi_bati", "targetname")[0].origin;
	yerler[1] = getentarray("karsi_dogu", "targetname")[0].origin;
	yerler[2] = getentarray("karsi_guney", "targetname")[0].origin;
	for (i = 0; i < yerler.size; i++)
	{
		org = spawn("script_origin", yerler[i] + (0, 0, 80));
		org playsound("walla_german_large");
		org thread gec_sil(12);
	}
}

gec_sil(sure)
{
	wait sure;
	self delete();
}

// 50 yaya: her 6 sn'de 5-7, uc yonden sirayla (spawner'lar sirayla: ust uste
// dogmasin). Dogus noktalari harita disi vadilerde: zorla dogur.
karsi_saldiri()
{
	yon = [];
	yon[0] = getentarray("karsi_bati", "targetname");
	yon[1] = getentarray("karsi_dogu", "targetname");
	yon[2] = getentarray("karsi_guney", "targetname");
	while (level.karsi_dogan < level.karsi_toplam)
	{
		parti = randomintrange(5, 8);           // 5-7
		for (k = 0; k < parti && level.karsi_dogan < level.karsi_toplam; k++)
		{
			grup = yon[level.karsi_dogan % 3];
			s = grup[int(level.karsi_dogan / 3) % grup.size];
			s.count = 1;
			guy = s stalingradspawn();
			if (spawn_failed(guy))
				continue;
			level.karsi_dogan++;
			guy.dogus = s.origin;
			guy thread karsi_saldirgan();
			wait 0.25;
		}
		wait 6;
	}
}

// karakola dogru siperden sipere ilerler, yakininda binaya yuklenir
karsi_saldirgan()
{
	self endon("death");
	self endon("kaciyor");
	hedef = (-150, 360, 0);
	wait randomfloatrange(0.3, 1.5);
	for (;;)
	{
		d = distance((self.origin[0], self.origin[1], 0), hedef);
		if (d < 800)
		{
			// kullanici: binanin alt ve ust katina yonelsinler
			n = level.bina_ic[randomint(level.bina_ic.size)];
			self.goalradius = 64;
			self setgoalpos(n.origin);
			self hedef_bekle(20);
			wait randomfloatrange(4, 8);
			continue;
		}
		adim = d - 400;
		if (adim > 600)
			adim = 600;
		ara = self.origin + vectorScale(vectornormalize(hedef - (self.origin[0], self.origin[1], 0)), adim);
		n = siper_bul(ara, 400);
		if (isdefined(n))
		{
			self.goalradius = 96;
			self setgoalnode(n);
		}
		else
		{
			self.goalradius = 256;
			self setgoalpos(ara);
		}
		self hedef_bekle(12);
		wait randomfloatrange(2, 5);
	}
}

siper_bul(nokta, en_cok)
{
	en = undefined;
	ed = en_cok;
	for (i = 0; i < level.siper.size; i++)
	{
		d = distance(level.siper[i].origin, nokta);
		if (d < ed)
		{
			en = level.siper[i];
			ed = d;
		}
	}
	return en;
}

// KARSI SALDIRI ARACLARI: once kamyon; 5 sn sonra yarim paletli (bati);
// onun MG nisancisi olunce 10 sn sonra ikinci yarim paletli (dogu)
arac_dalgasi()
{
	kamyon = maps\_vehicle::scripted_spawn(1);
	level thread maps\_vehicle::gopath(kamyon[0]);
	kamyon[0] thread inenler_saldirsin();
	wait 5;
	yp = maps\_vehicle::scripted_spawn(2);
	level thread maps\_vehicle::gopath(yp[0]);
	yp[0] thread inenler_saldirsin();
	wait 1;
	nisanci = mg_nisancisi(yp[0]);
	if (isdefined(nisanci))
		nisanci waittill("death");
	wait 10;
	yp2 = maps\_vehicle::scripted_spawn(3);
	level thread maps\_vehicle::gopath(yp2[0]);
	yp2[0] thread inenler_saldirsin();
	level.araclar_tamam = true;
}

// stok _halftrack: yer 1 = MG nisancisi (script_startingposition)
mg_nisancisi(arac)
{
	if (!isdefined(arac.riders))
		return undefined;
	for (i = 0; i < arac.riders.size; i++)
		if (isalive(arac.riders[i]) && isdefined(arac.riders[i].script_startingposition) && arac.riders[i].script_startingposition == 1)
			return arac.riders[i];
	return undefined;
}

// arac durunca inenler karakola saldirir (yarim paletlinin MG nisancisi kalir)
inenler_saldirsin()
{
	self waittill("reached_end_node");
	wait 5;
	if (!isdefined(self.riders))
		return;
	for (i = 0; i < self.riders.size; i++)
	{
		g = self.riders[i];
		if (!isalive(g) || !issentient(g))
			continue;
		if (isdefined(g.script_startingposition) && g.script_startingposition == 1 && issubstr(self.vehicletype, "halftrack"))
			continue;
		g.dogus = self.origin;
		g thread karsi_saldirgan();
	}
}

alman_kac()
{
	self endon("death");
	self notify("kaciyor");
	if (isdefined(self.script_startingposition) && self.script_startingposition == 1 && isdefined(self.script_vehicleride))
	{
		self delete();                          // MG nisancisi: arac terk edildi
		return;
	}
	self.health = 1;
	self.goalradius = 96;
	self allowedstances("stand");
	if (!isdefined(self.dogus))
		self.dogus = getentarray("karsi_guney", "targetname")[0].origin;
	self setgoalpos(self.dogus);
	self waittill("goal");
	self delete();
}

// --------------------------------------------------------------------------
// FINAL CEMBERI
// --------------------------------------------------------------------------
// Leonov merkezde; ekip etrafinda cember (guney bos: oyuncunun yeri), ortaya bakar
final_cember(merkez)
{
	level notify("daire");
	level.ekip_mod = "cember";
	g = level.leonov;
	g.goalradius = 24;
	g setgoalpos(merkez);
	ai = getaiarray("allies");
	digerleri = [];
	for (i = 0; i < ai.size; i++)
		if (ai[i] != g)
			digerleri[digerleri.size] = ai[i];
	n = digerleri.size + 1;                     // +1 oyuncunun yeri (guney, bos)
	level.oyuncu_yeri = merkez + (cos(270) * 150, sin(270) * 150, 0);
	for (i = 0; i < digerleri.size; i++)
	{
		a = 270 + 360.0 * (i + 1) / n;          // 270 (guney) oyuncuya bos kalir
		p = merkez + (cos(a) * 150, sin(a) * 150, 0);
		tr = bulletTrace(p + (0, 0, 200), p - (0, 0, 300), false, undefined);
		digerleri[i].goalradius = 16;
		digerleri[i].cember_yer = tr["position"];
		digerleri[i] setgoalpos(tr["position"]);
		digerleri[i] thread cember_bak(merkez);
	}
	g.cember_yer = merkez;
	g thread lider_bak();
	level.cember_ekip = digerleri;
	level.cember_ekip[level.cember_ekip.size] = g;
	// kullanici: isinlanma YOK. 60 sn'de varamayan asker beklenmez (yurumeye devam eder)
	wait 60;
	for (i = 0; i < level.cember_ekip.size; i++)
	{
		a = level.cember_ekip[i];
		if (isalive(a) && isdefined(a.cember_yer) && a != level.leonov &&
			distance((a.origin[0], a.origin[1], 0), (a.cember_yer[0], a.cember_yer[1], 0)) > 72)
			a.cember_yer = undefined;
	}
}

// Kullanici: sonda rastgele bir PPSh'li asker (Leonov haric) havaya 30 mermi
// atar, sonra sarjor degistirir. AI atisi stok animscripts utility.gsc kalibi
// (self shoot(isabet, hedef)); sarjor stok combat_utility Reload().
zafer_atesi()
{
	ai = getaiarray("allies");
	aday = [];
	for (i = 0; i < ai.size; i++)
		if (ai[i] != level.leonov && issubstr(tolower(ai[i].weapon), "ppsh"))
			aday[aday.size] = ai[i];
	if (!aday.size)
		return;
	g = aday[randomint(aday.size)];
	g endon("death");
	for (k = 0; k < 30; k++)
	{
		g shoot(1, g.origin + (randomintrange(-60, 60), randomintrange(-60, 60), 2000));
		wait 0.08;
	}
	g.bulletsInClip = 0;
	g animscripts\combat_utility::Reload(0);
}

// hayattaki herkes kendi cember yerinde mi
cember_hazir()
{
	if (!isdefined(level.cember_ekip))
		return false;
	for (i = 0; i < level.cember_ekip.size; i++)
	{
		g = level.cember_ekip[i];
		if (!isalive(g) || !isdefined(g.cember_yer))
			continue;
		if (distance((g.origin[0], g.origin[1], 0), (g.cember_yer[0], g.cember_yer[1], 0)) > 72)
			return false;
	}
	return true;
}

cember_bak(merkez)
{
	self endon("death");
	self hedef_bekle(20);
	for (;;)
	{
		self orientmode("face angle", vectortoangles(merkez - self.origin)[1]);
		wait 0.5;
	}
}

lider_bak()
{
	self endon("death");
	self hedef_bekle(20);
	for (;;)
	{
		self orientmode("face angle", vectortoangles(level.player.origin - self.origin)[1]);
		wait 0.5;
	}
}

// Konusma bitti: 7 sn'de karar, bolum tamamlanir
bolum_sonu()
{
	perde = newHudElem();
	perde.x = 0;
	perde.y = 0;
	perde.horzAlign = "fullscreen";
	perde.vertAlign = "fullscreen";
	perde.foreground = true;
	perde.alpha = 0;
	perde setshader("black", 640, 480);
	perde fadeOverTime(7);                      // kullanici: 7 sn
	perde.alpha = 1;
	wait 7.5;
	missionSuccess("credits", false);       // zincirin son halkasi (stok _endmission)
}

// --------------------------------------------------------------------------
// EKRAN TURU (kr_tur 1: genel/kus bakisi, kr_tur 3: bina ici ve mevziler)
// --------------------------------------------------------------------------
ekran_turu()
{
	level.player takeallweapons();
	nokta = [];
	aci = [];
	nokta[nokta.size] = (0, 0, 4200);        aci[aci.size] = (89, 90, 0);    // tum harita
	nokta[nokta.size] = (-150, 470, 1500);   aci[aci.size] = (89, 90, 0);    // A ust
	nokta[nokta.size] = (-2310, 1350, 1300); aci[aci.size] = (89, 90, 0);    // B ust
	nokta[nokta.size] = (2600, 1000, 1500);  aci[aci.size] = (89, 90, 0);    // C ust
	nokta[nokta.size] = (1400, 100, 1800);   aci[aci.size] = (89, 90, 0);    // dere + kopruler
	nokta[nokta.size] = (-2330, 1300, 300);  aci[aci.size] = (6, 237, 0);    // B'den bati vadisine
	nokta[nokta.size] = (2700, 1100, 320);   aci[aci.size] = (6, 301, 0);    // C'den dogu vadisine
	nokta[nokta.size] = (90, -2620, 210);    aci[aci.size] = (4, 211, 0);    // baslangictan kamyon yoluna
	nokta[nokta.size] = (1380, 300, 120);    aci[aci.size] = (25, 90, 0);    // dere suyu
	nokta[nokta.size] = (-150, -950, 260);   aci[aci.size] = (12, 90, 0);    // karakol dis cephe
	if (getcvar("kr_tur") == "3")
	{
		nokta = [];
		aci = [];
		nokta[nokta.size] = (-150, -60, 80);     aci[aci.size] = (0, 90, 0);    // giris
		nokta[nokta.size] = (-530, 300, 80);     aci[aci.size] = (10, 60, 0);   // komuta odasi
		nokta[nokta.size] = (230, 300, 80);      aci[aci.size] = (10, 60, 0);   // kogus
		nokta[nokta.size] = (-100, 250, 80);     aci[aci.size] = (5, 100, 0);   // hol + merdiven
		nokta[nokta.size] = (-254, 760, 290);    aci[aci.size] = (25, 270, 0);  // merdiven ustu
		nokta[nokta.size] = (-500, 600, 290);    aci[aci.size] = (5, 300, 0);   // ust bati
		nokta[nokta.size] = (230, 600, 290);     aci[aci.size] = (5, 270, 0);   // ust dogu pencere
		nokta[nokta.size] = (-2250, 1250, 290);  aci[aci.size] = (15, 150, 0);  // B havan
		nokta[nokta.size] = (2600, 900, 320);    aci[aci.size] = (15, 60, 0);   // C havan
		nokta[nokta.size] = (200, -2600, 200);   aci[aci.size] = (5, 90, 0);    // baslangic, yikik ev
	}
	setcvar("kr_adim", "0");
	wait 3;
	for (i = 0; i < nokta.size; i++)
	{
		setcvar("kr_adim", "" + (i + 1));
		for (t = 0; t < 200; t++)
		{
			level.player setorigin(nokta[i]);
			level.player setplayerangles(aci[i]);
			wait 0.05;
		}
	}
	setcvar("kr_adim", "bitti");
}

// --------------------------------------------------------------------------
// OTOMATIK TEST (kr_test 1): butun gorev akisini oynatir, her adimi
// konsola "TEST:" ile yazar. Normal oyunda calismaz.
// --------------------------------------------------------------------------
otomatik_test()
{
	level thread test_olumsuz();
	level waittill("tanitim_bitti");
	test_yaz("tanitim bitti");
	wait 10;
	level.player setorigin((-150, -60, 24));
	wait 3;
	test_oldur("karakol");
	flag_wait("a_temiz");
	test_yaz("A tamam, engel kalkti: " + !isdefined(level.engel_bc));
	wait 4;
	level.player setorigin((-2000, 700, 40));
	wait 8;
	test_oldur("mevzi_b");
	flag_wait("b_temiz");
	test_yaz("B tamam");
	level.player setorigin((2300, 400, 40));
	wait 8;
	test_oldur("mevzi_c");
	flag_wait("c_temiz");
	test_yaz("C tamam");
	wait 4;
	level.player setorigin((-150, 470, 40));
	for (;;)
	{
		wait 2;
		ai = getaiarray("axis");
		ic = 0;
		dost = getaiarray("allies");
		for (d = 0; d < dost.size; d++)
		{
			o = dost[d].origin;
			if (o[0] > -726 && o[0] < 426 && o[1] > 118 && o[1] < 822)
				ic++;
		}
		test_yaz("karsi " + level.karsi_dogan + " alman " + ai.size + " arac " + isdefined(level.araclar_tamam) + " evdeki dost " + ic + "/" + dost.size);
		if (flag("savunma_bitti"))
			break;
		for (i = 0; i < ai.size; i++)
		{
			if (level.karsi_dogan >= level.karsi_toplam && isdefined(level.araclar_tamam) && getaiarray("axis").size <= 6)
				break;
			if (isalive(ai[i]) && randomint(3) == 0)
				ai[i] dodamage(ai[i].health + 500, ai[i].origin);
		}
	}
	test_yaz("kacis basladi");
	wait 35;
	test_yaz("kacan kalan " + getaiarray("axis").size + " cember hazir " + cember_hazir());
	level.player setorigin(level.oyuncu_yeri + (0, 0, 8));
	level waittill("oyuncu_cemberde");
	test_yaz("oyuncu cemberde, final konusma");
}

test_yaz(msg)
{
	setcvar("kr_log", msg);                     // konsolda "dvar set kr_log ..." olarak kalir
	wait 0.05;
}

test_olumsuz()
{
	for (;;)
	{
		level.player.health = 1000;
		wait 0.1;
	}
}

test_oldur(grup)
{
	ai = getaiarray("axis");
	n = 0;
	for (i = 0; i < ai.size; i++)
		if (isdefined(ai[i].script_aigroup) && ai[i].script_aigroup == grup)
		{
			ai[i] dodamage(ai[i].health + 500, ai[i].origin);
			n++;
		}
	test_yaz("" + grup + " olduruldu " + n);
}

// kr_test 2: oyuncu yerinden kipirdamadan dost hareketini olcer
dost_olcum()
{
	level thread test_olumsuz();
	level waittill("tanitim_bitti");
	for (t = 0; t < 14; t++)
	{
		wait 5;
		ai = getaiarray("allies");
		for (i = 0; i < ai.size; i++)
		{
			hedef = "yok";
			if (isdefined(ai[i].goalpos))
				hedef = "" + ai[i].goalpos;
			test_yaz("t" + (t * 5) + " dost" + i + " " + ai[i].origin + " hedef " + hedef + " r " + ai[i].goalradius + " oyuncuya " + int(distance(ai[i].origin, level.player.origin)));
		}
		ax = getaiarray("axis");
		for (i = 0; i < ax.size && i < 4; i++)
			test_yaz("t" + (t * 5) + " alman" + i + " " + ax[i].origin);
		if (t == 2)
		{
			for (i = 0; i < ai.size; i++)
			{
				if (i % 2)
					continue;
				ai[i].goalradius = 128;
				if (i % 4 == 0)
					ai[i] setgoalpos((-150, 400, 24));  // bina ici konum
				else
					ai[i] setgoalnode(level.siper[0]);  // (karsilastirma)
			}
		}
		if (t == 6)
			level.player setorigin((60, -1500, 40));
	}
}

// kr_test 3: TANI -- takilan askerler, bina icine ulasim, arac yolculari
tani_olcum()
{
	level thread test_olumsuz();
	level waittill("tanitim_bitti");
	wait 2;
	level.player setorigin((60, -1700, 40));
	wait 20;
	ai = getaiarray("allies");
	for (i = 0; i < ai.size; i++)
		test_yaz("bas" + i + " " + ai[i].origin + " oyuncuya " + int(distance(ai[i].origin, level.player.origin)));
	// bina ici ulasim: herkese ic konum
	for (i = 0; i < ai.size; i++)
	{
		ai[i].goalradius = 64;
		ai[i] setgoalpos((-150, 400, 24));
	}
	level.player setorigin((-150, -400, 40));
	wait 30;
	for (i = 0; i < ai.size; i++)
		if (isalive(ai[i]))
			test_yaz("ic" + i + " " + ai[i].origin + " hedefe " + int(distance(ai[i].origin, (-150, 400, 24))));
	// araclar: yolcu sayisi
	for (g = 1; g <= 3; g++)
	{
		a = maps\_vehicle::scripted_spawn(g);
		wait 1;
		n = 0;
		if (isdefined(a[0].riders))
			n = a[0].riders.size;
		test_yaz("arac" + g + " yolcu " + n);
	}
	test_yaz("tani bitti");
}

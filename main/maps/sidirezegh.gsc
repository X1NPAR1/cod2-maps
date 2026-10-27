// sidirezegh.gsc -- "Son Kale", Sidi Rezegh yakinlari, Libya, 23 Kasim 1941 (bagimsiz bolum).
//
// AKIS (kullanici kararlari):
//   1) Oyuncu, Cpt. Price (olumsuz) ve 6 Ingiliz iki katli KARARGAHta; herkes pencerelere.
//   2) DALGA 1: 12 Alman (kuzey + dogu).                         30 sn nefes.
//   3) DALGA 2: 18 Alman + yari paletli MG (dogu).               30 sn nefes.
//   4) DALGA 3: 24 Alman + Panzer II (guney). Tank gorununce karargahin zemin katinda duvara
//      dayali, tam mermili bir Panzerschreck BELIRIR (oncesinde yok); almak gorev, sonra tanki vur.
//   5) Takviye: batidan iki Ingiliz kamyonu; Price meydanda halkada konusur, kararma, jenerik.
// Kaliplar: kumtepe (pencere savunmasi, dalga, yari paletli, tank atisi), crossroads (spawn
// "weapon_panzerschreck"), stock _load anahtarlari; skill: stock-scripts-study.
#include maps\_utility;
#include maps\_anim;

main()
{
	setExpFog(0.00022, .86, .74, .60, 0);       // ikindi, hafif tozlu
	setCullDist(14000);

	precacheString(&"SIDIREZEGH_OBJ_SAVUN");
	precacheString(&"SIDIREZEGH_OBJ_DALGA2");
	precacheString(&"SIDIREZEGH_OBJ_DALGA3");
	precacheString(&"SIDIREZEGH_OBJ_SCHRECK");
	precacheString(&"SIDIREZEGH_OBJ_PANZER");
	precacheString(&"SIDIREZEGH_OBJ_PRICE");
	precacheString(&"SIDIREZEGH_MSG_KURTARMA");
	precacheString(&"SIDIREZEGH_OBJ_KAMYON");
	precacheString(&"SIDIREZEGH_PLATFORM_KAMYON");
	precacheString(&"SIDIREZEGH_INTRO_TITLE");
	precacheString(&"SIDIREZEGH_INTRO_PLACE");
	precacheString(&"SIDIREZEGH_INTRO_DATE");
	precacheString(&"SIDIREZEGH_INTRO_INFO");
	precacheShader("black");
	precacheModel("xmodel/weapon_panzerschreck");
	precacheItem("panzerschreck");

	level.campaign = "british";
	level.totalfriends = 0;                     // _load'dan ONCE
	level.maxfriendlies = 0;
	maps\_truck::main("xmodel/vehicle_opel_blitz_desert");
	maps\_panzer2::main("xmodel/vehicle_panzer_ii");
	maps\_halftrack::main("xmodel/vehicle_halftrack_mg_desert");
	maps\_crusader::main("xmodel/vehicle_crusader2");
	maps\sidirezegh_fx::main();
	maps\_load::main();
	maps\sidirezegh_anim::main();

	level.ekip_mod = "bekle";
	flag_init("tanitim_bitti");
	flag_init("panzer_oldu");
	flag_init("bitti");

	level.sinir = maps\sidirezegh_sinir::cokgen();
	level.kare = [];
	level.kare[0] = (-1510, -1510, 0);             // surun ici
	level.kare[1] = (1510, -1510, 0);
	level.kare[2] = (1510, 1510, 0);
	level.kare[3] = (-1510, 1510, 0);
	// sur kapisi engelleri (clip_player) ve karargah kapisi derlemede +4000 yukarida (yol agi); oyunda yerinde
	e = getentarray("kapi_engel", "targetname");
	for (i = 0; i < e.size; i++)
		e[i] moveto(e[i].origin - (0, 0, 4000), 0.05);
	level.kapi = getent("karargah_kapi", "targetname");
	level.kapi moveto(level.kapi.origin - (0, 0, 4000), 0.05);
	level thread kapi_kapat();
	level.kamyon_tetik = getent("kamyon_bin", "targetname");
	level.kamyon_tetik tetik_kapat_ent();
	level.meydan = getent("meydan", "targetname").origin;
	level.karargah = getent("karargah", "targetname").origin;
	level.asama = "BASLANGIC";

	if (getcvar("kr_tur") == "1")
	{
		level thread ekran_turu();
		return;
	}
	oyuncu_techizat();
	siper_onbellek();
	anim.noWeaponToss = true;
	level.ekip = [];
	level.ingilizler = [];
	level.dalga_ai = [];
	level thread sinir_bekcisi();
	level thread siper_denetci();
	if (getcvar("kr_tur") == "2")
		level thread akis_testi();
	level thread gorevler();
}

tanitim()
{
	level.introblack = newHudElem();
	level.introblack.x = 0;
	level.introblack.y = 0;
	level.introblack.horzAlign = "fullscreen";
	level.introblack.vertAlign = "fullscreen";
	level.introblack.foreground = true;
	level.introblack setShader("black", 640, 480);
	musicplay("sidirezegh_muzik_giris");
	wait .05;
	level.introstring = [];
	maps\_introscreen::introscreen_create_line(&"SIDIREZEGH_INTRO_TITLE");
	wait 2;
	maps\_introscreen::introscreen_create_line(&"SIDIREZEGH_INTRO_PLACE");
	maps\_introscreen::introscreen_create_line(&"SIDIREZEGH_INTRO_DATE");
	wait 2;
	maps\_introscreen::introscreen_create_line(&"SIDIREZEGH_INTRO_INFO");
	wait 3;
	level.introblack fadeOverTime(3);
	level.introblack.alpha = 0;
	maps\_introscreen::introscreen_fadeOutText();
	flag_set("tanitim_bitti");
}

// durbunlu Lee-Enfield + Thompson, 4 el bombasi, 2 duman
oyuncu_techizat()
{
	level.player takeallweapons();
	level.player giveWeapon("enfield_scope");     // kullanici: birincil durbunlu Lee-Enfield
	level.player giveWeapon("thompson");          // ikincil Thompson
	level.player giveWeapon("MK1britishfrag");
	level.player giveWeapon("smoke_grenade_american");
	level.player giveMaxAmmo("enfield_scope");
	level.player giveMaxAmmo("thompson");
	level.player setWeaponClipAmmo("MK1britishfrag", 4);
	level.player setWeaponClipAmmo("smoke_grenade_american", 2);
	level.player switchToWeapon("enfield_scope");
	level.player switchToOffhand("MK1britishfrag");
	maps\_loadout::setup_british_africa();
}

// --------------------------------------------------------------------------
// GOREV AKISI
// --------------------------------------------------------------------------
gorevler()
{
	level thread tanitim();
	ingilizleri_dogur();
	objective_add(1, "active", &"SIDIREZEGH_OBJ_SAVUN", level.karargah);
	objective_current(1);
	savunmaya_gec(tum_ingilizler());
	flag_wait("tanitim_bitti");
	level thread autoSaveByName("baslangic");
	// kullanici: once Price konusur, sonra saldiri baslar
	price_der("giris");
	price_der("savun");
	level thread muzik("sidirezegh_muzik_savunma");
	wait 6;

	// kullanici: toplam 60 Alman (yolcular dahil), 2 yari paletli, 1 kamyon, son dalgada Panzer
	// --- DALGA 1: 15 = 6 piyade + Alman kamyonu (9 kisi, kuzey)
	level.asama = "DALGA1";
	level.dalga_ai = [];
	level.bekleyen_arac = 0;
	level thread arac_saldirisi(5, "alman_kamyon", false);
	dalga(20, "kuzey", "dogu", undefined);
	dalga_bitsin();
	level thread autoSaveByName("dalga1");
	wait 25;

	// --- DALGA 2: 20 = 11 piyade + yari paletli (9 kisi, dogu)
	level.asama = "DALGA2";
	objective_add(2, "active", &"SIDIREZEGH_OBJ_DALGA2", level.karargah);
	objective_current(2);
	level.dalga_ai = [];
	level thread arac_saldirisi(1, "yarim", true);
	dalga(30, "dogu", "guney", "kuzey");
	dalga_bitsin();
	objective_state(2, "done");
	level thread autoSaveByName("dalga2");
	wait 25;

	// --- DALGA 3: 25 = 16 piyade + ikinci yari paletli (9 kisi, dogu) + Panzer (guney)
	level.asama = "DALGA3";
	objective_add(3, "active", &"SIDIREZEGH_OBJ_DALGA3", level.karargah);
	objective_current(3);
	level thread muzik("sidirezegh_muzik_tank");
	level.dalga_ai = [];
	level thread arac_saldirisi(6, "yarim2", true);
	level thread panzer_saldirisi();
	dalga(40, "guney", "kuzey", "dogu");
	flag_wait("panzer_oldu");
	dalga_bitsin();
	objective_state(3, "done");
	objective_state(1, "done");
	level thread autoSaveByName("dalga3");

	// --- FINAL: Price kapiyi tekmeyle acar, kamyon evin onunde, binilir, haritadan cikilir
	level thread muzik_bir("sidirezegh_muzik_kurtulus");
	final_cikis();
}

// --------------------------------------------------------------------------
// INGILIZLER: Price (olumsuz) + 6 (1450 can), pencere savunmasi (kumtepe kalibi)
// --------------------------------------------------------------------------
ingilizleri_dogur()
{
	sp = getentarray("price", "targetname");
	level.price = dogur(sp[0]);
	sp[0] delete();
	level.price.animname = "price";
	level.price thread magic_bullet_shield();
	level.ekip[level.ekip.size] = level.price;
	sp = getentarray("ingiliz", "targetname");
	for (i = 0; i < sp.size; i++)
	{
		g = dogur(sp[i]);
		sp[i] delete();
		if (!isdefined(g))
			continue;
		g.health = 100;                             // kullanici: Price olumsuz, digerleri 100 can
		g.maxhealth = 100;
		level.ekip[level.ekip.size] = g;
	}
}

tum_ingilizler()
{
	t = [];
	for (i = 0; i < level.ekip.size; i++)
		if (isalive(level.ekip[i]))
			t[t.size] = level.ekip[i];
	for (i = 0; i < level.ingilizler.size; i++)
		if (isalive(level.ingilizler[i]))
			t[t.size] = level.ingilizler[i];
	return t;
}

savunmaya_gec(liste)
{
	liste = karistir(liste);
	// kullanici: Price alt katta
	if (isdefined(level.price) && isalive(level.price))
	{
		alt = bos_pencereler("0");
		if (alt.size)
		{
			alt[0].dolu = true;
			level.price.siper_ent = alt[0];
			level.price thread siper_al(alt[0].origin, true);
		}
	}
	n = 0;
	for (i = 0; i < liste.size; i++)
	{
		g = liste[i];
		if (g == level.price)
			continue;
		yerler = bos_pencereler("" + (n % 2));     // kullanici: rastgele alt kat / ust kat
		if (!yerler.size)
			yerler = bos_pencereler(undefined);
		if (!yerler.size)
			break;
		n++;
		yer = yerler[0];
		yer.dolu = true;
		g.siper_ent = yer;
		g thread siper_al(yer.origin, true);
	}
}

bos_pencereler(kat)
{
	pen = [];
	e = getentarray("pencere", "targetname");
	for (i = 0; i < e.size; i++)
		if (!isdefined(e[i].dolu) && (!isdefined(kat) || e[i].script_noteworthy == kat))
			pen[pen.size] = e[i];
	return karistir(pen);
}

karistir(d)
{
	for (i = d.size - 1; i > 0; i--)
	{
		j = randomint(i + 1);
		t = d[i];
		d[i] = d[j];
		d[j] = t;
	}
	return d;
}

dizi_bas_sil(d)
{
	y = [];
	for (i = 1; i < d.size; i++)
		y[y.size] = d[i];
	return y;
}

// hemen: tanitim karartmasinda dogrudan pencereye (kullanici: alt katta ayakta kalan askerler --
// ust kata yol bagi tek yonlu, olculdu; oyuncu bakarken isinlama yapilamiyordu)
siper_al(yer, hemen)
{
	self endon("death");
	self notify("yeni_emir");
	self endon("yeni_emir");
	self.siper_yeri = yer;
	if (isdefined(hemen) && hemen)
		self teleport(yer);
	self allowedstances("stand", "crouch");
	self.goalradius = 12;
	self.suppressionwait = 0.5;
	n = pencere_dugumu(yer);
	if (isdefined(n))
		self setgoalnode(n);
	else
		self setgoalpos(yer);
	son = self.origin;
	bekle = 0;
	for (t = 0; t < 160; t++)
	{
		wait 0.5;
		if (distance(self.origin, yer) < 40)
			break;
		if (distance(self.origin, son) < 24)
			bekle++;
		else
			bekle = 0;
		son = self.origin;
		if (bekle >= 8 && !gorunur(self.origin) && !gorunur(yer))
		{
			self teleport(yer);
			break;
		}
	}
	if (isdefined(n))
		self setgoalnode(n);
	else
		self setgoalpos(yer);
	self.pathenemyfightdist = 64;                   // pencereden ayrilmaz
	self.pathenemylookahead = 64;
	self thread vurulunca_pencere();
	for (;;)
	{
		wait randomfloatrange(30, 40);              // sabit durmasin: baska pencereye
		self yer_degistir();
	}
}

yer_degistir()
{
	kat = "0";                                      // yer degistirme ayni katta (merdiven yalniz asagi bagli)
	if (isdefined(self.siper_ent))
		kat = self.siper_ent.script_noteworthy;
	aday = bos_pencereler(kat);
	if (!aday.size)
		return;
	yeni = aday[0];
	if (isdefined(self.siper_ent))
		self.siper_ent.dolu = undefined;
	yeni.dolu = true;
	self.siper_ent = yeni;
	self.siper_yeri = yeni.origin;
	self.goalradius = 16;
	n = pencere_dugumu(yeni.origin);
	if (isdefined(n))
		self setgoalnode(n);
	else
		self setgoalpos(yeni.origin);
}

// pencerenin arkasindaki siper dugumu (node_cover_stand, ent_sidirezegh)
pencere_dugumu(p)
{
	if (p[2] > 150)
		return undefined;                       // ust kat pencere dugumleri tek yonlu bagli (olculdu): konuma git
	en = undefined;
	ed = 40;
	for (i = 0; i < level.siper.size; i++)
	{
		d = distance(level.siper[i].origin, p);
		if (d < ed)
		{
			en = level.siper[i];
			ed = d;
		}
	}
	return en;
}

vurulunca_pencere()
{
	self endon("death");
	self endon("yeni_emir");
	son = gettime();
	for (;;)
	{
		self waittill("damage");
		if (gettime() - son < 6000)
			continue;
		son = gettime();
		wait randomfloatrange(0.3, 0.9);
		self yer_degistir();
	}
}

// --------------------------------------------------------------------------
// ALMANLAR
// --------------------------------------------------------------------------
dogur(sp)
{
	for (t = 0; t < 80; t++)
	{
		if (getaiarray().size < 30)
		{
			sp.count = 1;
			g = sp stalingradspawn();
			if (!spawn_failed(g))
				return g;
		}
		wait 0.5;
	}
	return undefined;
}

gorunur(p)
{
	goz = level.player.origin + (0, 0, 60);
	ileri = anglestoforward(level.player getplayerangles());
	fark = vectornormalize((p[0], p[1], p[2] + 40) - goz);
	if (vectordot(ileri, fark) < 0.35)
		return false;
	return sighttracepassed(goz, p + (0, 0, 48), false, undefined);
}

gizli_dogur(liste, en_az)
{
	for (t = 0; t < 60; t++)
	{
		aday = [];
		for (i = 0; i < liste.size; i++)
		{
			s = liste[i];
			if (distance(s.origin, level.player.origin) < en_az)
				continue;
			if (t < 40 && gorunur(s.origin))
				continue;
			aday[aday.size] = s;
		}
		if (aday.size && getaiarray().size < 30)
		{
			s = aday[randomint(aday.size)];
			s.count = 1;
			g = s stalingradspawn();
			if (!spawn_failed(g))
				return g;
		}
		wait 0.5;
	}
	return undefined;
}

// adet Alman, verilen yonlerden (sirayla); Price yonu soyler
dalga(adet, y1, y2, y3)
{
	yonler = [];
	yonler[0] = y1;
	yonler[1] = y2;
	if (isdefined(y3))
		yonler[2] = y3;
	sp = getentarray("dalga", "targetname");
	level.dalga_dogan = 0;
	level.dalga_hedef = adet;
	for (k = 0; k < adet; k++)
	{
		y = yonler[k % yonler.size];
		if (k < yonler.size)
			level thread price_der(y);
		sec = [];
		for (i = 0; i < sp.size; i++)
			if (sp[i].script_noteworthy == y)
				sec[sec.size] = sp[i];
		while (getaiarray("axis").size >= 22)
			wait 0.5;
		g = gizli_dogur(sec, 1500);
		if (!isdefined(g))
		{
			k--;
			wait 1;
			continue;
		}
		level.dalga_ai[level.dalga_ai.size] = g;
		level.dalga_dogan++;
		g thread saldiran_alman();
		wait randomfloatrange(0.4, 1.2);
	}
}

// dalganin tamami (yolcular dahil) olene kadar; son 2 inatci 60 sn sonra gorulmeden silinir
dalga_bitsin()
{
	az = 0;
	for (;;)
	{
		n = canli_say(level.dalga_ai) + level.bekleyen_arac;
		if (n == 0)
			return;
		if (n <= 2)
			az++;
		else
			az = 0;
		if (az > 60)
		{
			for (i = 0; i < level.dalga_ai.size; i++)
				if (isalive(level.dalga_ai[i]) && !gorunur(level.dalga_ai[i].origin))
					level.dalga_ai[i] delete();
		}
		wait 1;
	}
}

// kosarak meydana girer; vurulursa durup catisir; meydanda en yakin Ingilize/oyuncuya yuklenir
saldiran_alman()
{
	self endon("death");
	self.health = 100;
	self.maxhealth = 100;
	self.pathenemyfightdist = 0;
	self.pathenemylookahead = 0;
	self.ignoresuppression = true;
	self.goalradius = 120;
	self thread vurulunca_dur();
	s = getentarray("meydan_siper", "targetname");
	giris = zemin_bul(s[randomint(s.size)].origin);
	for (t = 0; t < 200 && distance(self.origin, level.meydan) > 1300; t++)
	{
		self setgoalpos(giris);
		wait 0.5;
	}
	self notify("meydana_girdi");
	self.pathenemyfightdist = 220;
	self.pathenemylookahead = 220;
	for (;;)
	{
		// kapilar kapali: karargahin cevresinde 450-900 arasi bir siper; ara sira yer degistirir
		yon = vectornormalize((self.origin[0], self.origin[1], 0) - (level.karargah[0], level.karargah[1], 0));
		uzak = randomfloatrange(450, 900);
		p = level.karargah + vectorScale(yon, uzak) + (randomfloatrange(-200, 200), randomfloatrange(-200, 200), 0);
		self.goalradius = 120;
		siper = siper_bul(p, 300);
		if (isdefined(siper))
			self setgoalnode(siper);
		else
			self setgoalpos(zemin_bul(p));
		wait randomfloatrange(4, 7);
	}
}

vurulunca_dur()
{
	self endon("death");
	self endon("meydana_girdi");
	for (;;)
	{
		self waittill("damage");
		self.pathenemyfightdist = 700;
		self.pathenemylookahead = 700;
		self.ignoresuppression = false;
		wait 4;
		self.pathenemyfightdist = 0;
		self.pathenemylookahead = 0;
		self.ignoresuppression = true;
	}
}

// ALMAN ARACI (kamyon / yari paletli): 8 yolcu; kapi agzinda durur, iner, saldirir; MG susmaz
arac_saldirisi(grup, ad, mg)
{
	level.bekleyen_arac++;
	wait randomfloatrange(4, 10);
	arac_yolcu_hazirla(grup, ad, 22);
	a = maps\_vehicle::scripted_spawn(grup);
	h = a[0];
	yolcu = [];
	if (isdefined(h.riders))
		yolcu = h.riders;
	for (i = 0; i < yolcu.size; i++)
		level.dalga_ai[level.dalga_ai.size] = yolcu[i];
	level.bekleyen_arac--;
	for (i = 0; i < yolcu.size; i++)
		if (isalive(yolcu[i]))
		{
			yolcu[i].health = 100;
			yolcu[i].maxhealth = 100;
		}
	if (ad == "yarim")
		kapi_engeli("kapi_d", 4000);                // kullanici: doguya yonelen yari paletli kasabaya girer
	level thread maps\_vehicle::gopath(h);
	if (ad == "alman_kamyon")
		h setspeed(20, 8);
	else
		h setspeed(14, 6);
	if (ad == "yarim")
		level thread kapi_gecince(h, "kapi_d");
	h waittill("reached_end_node");
	wait 3;
	if (mg && isdefined(h.mgturret) && isdefined(h.mgturret[0]))
	{
		h.mgturret[0] setturretteam("axis");
		h.mgturret[0] setmode("auto_nonai");
	}
	for (i = 0; i < yolcu.size; i++)
		if (isalive(yolcu[i]))
			yolcu[i] thread saldiran_alman();
}

arac_yolcu_hazirla(binen, ad, sinir)
{
	for (t = 0; t < 30; t++)
	{
		if (getaiarray().size <= sinir)
			break;
		wait 1;
	}
	sp = getentarray(ad + "_asker", "targetname");
	ai = [];
	for (i = 0; i < sp.size; i++)
	{
		sp[i].count = 1;
		g = sp[i] stalingradspawn();
		if (spawn_failed(g))
			continue;
		ai[ai.size] = g;
	}
	for (i = 0; i < sp.size; i++)
		sp[i] delete();
	level.script_vehicleridespawners[binen] = [];
	level.script_vehiclerideai[binen] = ai;
}

// --------------------------------------------------------------------------
// PANZER + PANZERSCHRECK (kullanici: tank gelmeden silah yok; gelince duvara dayali belirir,
// tam mermi; almak gorev; iki roket isabeti tanki yok eder)
// --------------------------------------------------------------------------
panzer_saldirisi()
{
	wait 20;
	kapi_engeli("kapi_g", 4000);                  // clip_player araci da durdurur: Panzer girerken kalkar
	a = maps\_vehicle::scripted_spawn(2);
	p = a[0];
	level.panzer = p;
	p thread panzer_zirh();
	p thread panzer_olum();
	level thread maps\_vehicle::gopath(p);
	while (isdefined(p) && !flag("panzer_oldu") && distance((p.origin[0], p.origin[1], 0), (0, 0, 0)) > 3000)
		wait 0.3;
	level thread asker_der("panzer");
	level thread panzerschreck_belir();
	while (isdefined(p) && !flag("panzer_oldu") && distance((p.origin[0], p.origin[1], 0), (0, 0, 0)) > 1000)
		wait 0.2;
	kapi_engeli("kapi_g", 0 - 4000);
	if (!isdefined(p) || flag("panzer_oldu"))
		return;                                     // kasabaya girmeden vuruldu
	p.durdu = true;
	p thread panzer_ates();
	p thread panzer_tur();
}

// kullanici: Panzer karargahin cevresinde dongu halinde tur atar, her dugumde 5 sn durur
panzer_tur()
{
	self endon("death");
	self endon("ates_dur");
	n = getvehiclenode("panzer_halka", "targetname");
	for (;;)
	{
		while (distance((self.origin[0], self.origin[1], 0), (n.origin[0], n.origin[1], 0)) > 70)
			wait 0.05;
		self setspeed(0, 10);
		wait 5;
		self resumespeed(4);
		if (!isdefined(n.target))
			return;
		n = getvehiclenode(n.target, "targetname");
	}
}

panzer_olum()
{
	self waittill("death");
	self notify("ates_dur");
	if (!flag("panzer_oldu"))
		flag_set("panzer_oldu");
}

kapi_gecince(h, ad)
{
	while (isdefined(h) && distance((h.origin[0], h.origin[1], 0), (0, 0, 0)) > 1300)
		wait 0.2;
	kapi_engeli(ad, 0 - 4000);
}

kapi_engeli(ad, dz)
{
	b = getentarray("kapi_engel", "targetname");
	for (i = 0; i < b.size; i++)
		if (b[i].script_noteworthy == ad)
			b[i] moveto(b[i].origin + (0, 0, dz), 0.05);
}

panzerschreck_belir()
{
	y = getent("panzerschreck_yer", "targetname");
	level.schreck = spawn("weapon_panzerschreck", y.origin, 1);        // crossroads kalibi (askida)
	level.schreck.angles = (-74, 90, 0);                               // duvara dayali
	objective_add(4, "active", &"SIDIREZEGH_OBJ_SCHRECK", y.origin);
	objective_current(4);
	while (!level.player hasweapon("panzerschreck"))
		wait 0.2;
	level.player giveMaxAmmo("panzerschreck");                         // kullanici: tam mermili
	objective_state(4, "done");
	objective_add(5, "active", &"SIDIREZEGH_OBJ_PANZER", level.panzer.origin);
	objective_current(5);
	level thread panzer_obj();
	flag_wait("panzer_oldu");
	objective_state(5, "done");
	level thread asker_der("tamam");
}

panzer_obj()
{
	while (!flag("panzer_oldu"))
	{
		if (isdefined(level.panzer))
			objective_position(5, level.panzer.origin);
		wait 0.3;
	}
}

// yalniz oyuncunun roketi isler: 2 isabet; piyade atesi ve el bombasi isler degil
panzer_zirh()
{
	self endon("death");
	isabet = 0;
	for (;;)
	{
		self.health = 100000;
		self waittill("damage", miktar, saldiran);
		if (!isdefined(saldiran) || saldiran != level.player)
			continue;
		if (level.player getcurrentweapon() != "panzerschreck" || miktar < 200)
			continue;
		isabet++;
		earthquake(0.4, 0.8, self.origin, 1500);
		if (isabet >= 2)
			break;
	}
	self notify("ates_dur");
	self.health = 1;
	self dodamage(50000, self.origin);
	self notify("death");
	if (!flag("panzer_oldu"))
		flag_set("panzer_oldu");
}

panzer_ates()
{
	self endon("death");
	self endon("ates_dur");
	hedef = getentarray("tank_hedef", "targetname");
	wait randomfloatrange(1, 2.5);
	for (;;)
	{
		if (randomint(3) == 0)
		{
			t = spawn("script_origin", level.player.origin + (randomfloatrange(-220, 220), randomfloatrange(-220, 220), 30));
			self tank_vur(t);
			t delete();
		}
		else
			self tank_vur(hedef[randomint(hedef.size)]);
		wait randomfloatrange(6, 9);
	}
}

tank_vur(hedef)
{
	self endon("death");
	self setturrettargetent(hedef, (0, 0, 0));
	self waittill_turret(6);
	self notify("turret_fire");
	wait 0.3;
	self clearturrettarget();
}

waittill_turret(sure)
{
	self endon("turret_on_target");
	wait 3;
}

// --------------------------------------------------------------------------
// FINAL (kullanici): Price alt kat kapisini tekmeyle acar (stok beltot chateau_kickdoor1, "kick"
// notetrack); Ingiliz kamyonu bati kapisindan gelip evin onunde bekler; Price stok beltot sahnesiyle
// surucuye biner; "kamyona bin" gorevi; 4 Ingiliz kasaya tirmanir; binince tum gorunmez duvarlar
// kalkar; kamyon haritadan cikar; Price konusur, konusma bitmeden 2 sn once 5 sn kararma.
// --------------------------------------------------------------------------
kapi_kapat()
{
	wait 0.2;
	level.kapi disconnectpaths();
}

final_cikis()
{
	level.asama = "FINAL";
	level.ekip_mod = "sahne";
	tum = tum_ingilizler();
	for (i = 0; i < tum.size; i++)
		tum[i] notify("yeni_emir");
	if (isdefined(level.panzer))
		level.panzer delete();                      // halka yolunda enkaz kalmasin (kamyon cikisi)
	// kullanici: kapi kirilmadan once kamyon dogar ve gelmeye baslar
	level thread kamyon_gelsin();
	n = getent("kapi_tekme", "targetname");
	level.price.goalradius = 16;
	level.price allowedstances("stand");
	n maps\_anim::anim_reach_solo(level.price, "tekme");
	for (w = 0; w < 300 && !(isdefined(level.kurtarma) && distance(level.kurtarma.origin, (0, -880, level.kurtarma.origin[2])) < 1100); w++)
		wait 0.1;
	n thread maps\_anim::anim_single_solo(level.price, "tekme");
	level.price kick_bekle(4);
	level.kapi moveto(level.kapi.origin - (0, 12, 0), 0.05);   // mentese dis yuze: kanat duvara gomulmez
	wait 0.05;
	level.kapi rotateyaw(0 - 100, 0.6, 0.01, 0.55);
	level.kapi playsound("wood_door_kick");
	level thread koridor_kur();
	wait 0.65;
	level.kapi connectpaths();
	test_yaz("kapi acildi");
	// kasaya binecek 4 Ingiliz
	binen = [];
	while (!isdefined(level.kamyon_durdu))
		wait 0.2;
	tum = tum_ingilizler();
	for (i = 0; i < tum.size && binen.size < 4; i++)
		if (tum[i] != level.price && !(isdefined(level.surucu) && tum[i] == level.surucu))
			binen[binen.size] = tum[i];
	level.binen_liste = binen;
	for (i = 0; i < binen.size; i++)
	{
		if (isdefined(level.surucu) && binen[i] == level.surucu)
			continue;
		binen[i] thread magic_bullet_shield();
		binen[i].goalradius = 64;
		binen[i] setgoalpos(zemin_bul((randomfloatrange(-120, 120), -420 - randomfloat(60), 0)));
	}
	while (!isdefined(level.kamyon_durdu))
		wait 0.2;
	k = level.kurtarma;
	price_der("kamyon");
	// Price surucu koltuguna (stok beltot McGregor sahnesi, kamyon kapisi animasyonuyla)
	level.price.goalradius = 16;
	k maps\_anim::anim_reach_solo(level.price, "truckscene", "tag_driver", undefined, k);
	level.price.allowdeath = 0;
	k thread maps\sidirezegh_anim::kamyon_kapi_sahnesi();
	k maps\_anim::anim_single_solo(level.price, "truckscene", "tag_driver", undefined, k);
	level.price linkto(k, "tag_driver");
	k thread maps\_anim::anim_loop_solo(level.price, "drive_loop", "tag_driver", "stop_idle");
	test_yaz("price surucude");
	// Ingilizler kasaya
	level.kasaya_binen = 0;
	for (i = 0; i < binen.size; i++)
		binen[i] thread kasaya_bin(k, i);
	// oyuncu: kamyona bin
	level.asama = "BIN";
	objective_add(7, "active", &"SIDIREZEGH_OBJ_KAMYON", k.origin);
	objective_current(7);
	t = level.kamyon_tetik;
	t tetik_ac();
	arka = k.origin - vectorScale(anglestoforward(k.angles), 175);
	t.origin = t.origin + ((arka[0], arka[1], 0) - (0, -610, 0));   // kullanici: tetik kasanin tam arkasinda
	t sethintstring(&"SIDIREZEGH_PLATFORM_KAMYON");
	t waittill("trigger");
	level.kamyon_tetik = undefined;
	t delete();
	objective_state(7, "done");
	oyuncu_kasaya(k);
	// binince: tum gorunmez duvarlar kalkar
	level notify("sinir_kalk");
	if (isdefined(level.koridor))
		for (i = 0; i < level.koridor.size; i++)
			level.koridor[i] moveto(level.koridor[i].origin + (0, 0, 4000), 0.05);
	e = getentarray("kapi_engel", "targetname");
	for (i = 0; i < e.size; i++)
		e[i] moveto(e[i].origin + (0, 0, 4000), 0.05);
	for (w = 0; w < 60 && level.kasaya_binen < binen.size; w++)
		wait 0.25;
	level.asama = "CIKIS";
	level thread muzik_bir("sidirezegh_muzik_final");
	k resumespeed(3);
	level thread kamyon_hizlan(k);
	wait 2;
	// Price konusur (9.4 sn); bitmesinden 2 sn once 5 sn kararma
	level thread price_der("final1");
	wait 7.4;
	bolum_sonu(5);
}

// kullanici: yumusak kalkis, yola (sur disina) cikinca hizlanir
kamyon_hizlan(k)
{
	k endon("death");
	while (abs(k.origin[1]) < 1600)
		wait 0.1;
	k setspeed(24, 6);
}

kick_bekle(sure)
{
	self endon("death");
	self thread kick_zaman(sure);
	self waittillmatch("single anim", "kick");
}

kick_zaman(sure)
{
	wait sure;
	self notify("single anim", "kick");
}

kamyon_gelsin()
{
	b = getentarray("kapi_engel", "targetname");
	for (i = 0; i < b.size; i++)
		if (b[i].script_noteworthy == "kapi_b")
			b[i] moveto(b[i].origin + (0, 0, 4000), 0.05);
	arac_yolcu_hazirla(3, "kurtarma", 28);
	a = maps\_vehicle::scripted_spawn(3);
	k = a[0];
	level.kurtarma = k;
	level.kasadakiler = [];
	if (isdefined(k.riders) && k.riders.size)
	{
		level.surucu = k.riders[0];
		level.surucu thread magic_bullet_shield();
		for (i = 1; i < k.riders.size; i++)
			if (isalive(k.riders[i]))
			{
				k.riders[i].health = 100;
				k.riders[i].maxhealth = 100;
				level.kasadakiler[level.kasadakiler.size] = k.riders[i];
			}
	}
	k thread arac_olumsuz();
	level thread maps\_vehicle::gopath(k);
	k setspeed(26, 8);                              // kullanici: cok yavas geliyordu
	while (distance((k.origin[0], k.origin[1], 0), (0, 0, 0)) > 1750)
		wait 0.1;
	k setspeed(10, 8);                              // sehre girince yavaslar
	durak = (0, -880, 0);
	while (distance((k.origin[0], k.origin[1], 0), durak) > 70)
		wait 0.05;
	k setspeed(0, 6);
	wait 2;
	k notify("unload");                             // sofor iner (stok _vehicle unload)
	wait 4;
	if (isdefined(level.surucu) && isalive(level.surucu))
		level.surucu thread kapi_nobetcisi(k);
	level thread karargahi_tut();
	level thread crusaderlar();
	b = getentarray("kapi_engel", "targetname");
	for (i = 0; i < b.size; i++)
		if (b[i].script_noteworthy == "kapi_b")
			b[i] moveto(b[i].origin - (0, 0, 4000), 0.05);
	level.kamyon_durdu = true;
	test_yaz("kamyon evin onunde");
}

// kullanici: bir asker acik kapinin onunde kamyona bakarak nobet tutar
kapi_nobetcisi(k)
{
	self endon("death");
	self notify("yeni_emir");
	self allowedstances("stand");
	self.goalradius = 16;
	self setgoalpos(zemin_bul((40, -300, 0)));
	self hedef_bekle(15);
	m = spawn("script_origin", k.origin + (0, 0, 60));
	for (;;)
	{
		if (isdefined(level.kurtarma))
			m.origin = level.kurtarma.origin + (0, 0, 60);
		self lookat(m, 1.2);
		wait 1;
	}
}

// kasadan inen 5 asker + kamyona binmeyen ekip karargah pencerelerine siper alir
karargahi_tut()
{
	while (!isdefined(level.binen_liste))
		wait 0.2;
	e = getentarray("pencere", "targetname");
	for (i = 0; i < e.size; i++)
		e[i].dolu = undefined;
	liste = level.kasadakiler;
	tum = tum_ingilizler();
	for (i = 0; i < tum.size; i++)
	{
		g = tum[i];
		if (g == level.price || (isdefined(level.surucu) && g == level.surucu) || esit_var(level.binen_liste, g) || esit_var(liste, g))
			continue;
		liste[liste.size] = g;
	}
	for (i = 0; i < liste.size; i++)
	{
		if (!isalive(liste[i]))
			continue;
		y = bos_pencereler("" + (i % 2));
		if (!y.size)
			y = bos_pencereler(undefined);
		if (!y.size)
			break;
		y[0].dolu = true;
		liste[i].siper_ent = y[0];
		liste[i] thread siper_al(y[0].origin);
	}
}

esit_var(d, e)
{
	for (i = 0; i < d.size; i++)
		if (d[i] == e)
			return true;
	return false;
}

// kullanici: kapi kirilinca evin koselerinden sur kapisina kadar koridor (kamyon gectikten sonra)
koridor_kur()
{
	for (w = 0; w < 400; w++)
	{
		if (isdefined(level.kamyon_durdu) || (isdefined(level.kurtarma) && level.kurtarma.origin[0] > -200))
			break;
		wait 0.1;
	}
	level.koridor = getentarray("final_koridor", "targetname");
	for (i = 0; i < level.koridor.size; i++)
		level.koridor[i] moveto(level.koridor[i].origin - (0, 0, 4000), 0.05);
}

eski_surucu_izle(k)
{
	self endon("death");
	self notify("yeni_emir");
	sag = anglestoright(k.angles);
	self.goalradius = 24;
	self setgoalpos(zemin_bul(k.origin + vectorScale(sag, 0 - 220) + vectorScale(anglestoforward(k.angles), 60)));
	self hedef_bekle(8);
	for (;;)
	{
		if (isdefined(level.price))
			self lookat(level.price, 1.5);
		wait 1;
	}
}

// kullanici: Price kapiyi kirinca 3 sn arayla 5 Crusader (biri kasabada, digerleri disarida)
crusaderlar()
{
	wait 5;
	for (i = 0; i < 5; i++)
	{
		a = maps\_vehicle::scripted_spawn(7 + i);
		c = a[0];
		c thread arac_olumsuz();
		level thread maps\_vehicle::gopath(c);
		c setspeed(18, 6);
		if (i == 0)
			level thread crusader_bati_kapi(c);
		wait 3;
	}
}

// koyun icine giren Crusader bati kapisindan gecer (engel gecici kalkar)
crusader_bati_kapi(c)
{
	kapi_engeli("kapi_b", 4000);
	while (isdefined(c) && distance((c.origin[0], c.origin[1], 0), (0, 0, 0)) > 1300)
		wait 0.2;
	kapi_engeli("kapi_b", 0 - 4000);
}

arac_olumsuz()
{
	self endon("death");
	for (;;)
	{
		self.health = 100000;
		self waittill("damage");
	}
}

oyuncu_kasaya(k)
{
	ileri = anglestoforward(k.angles);
	arka = k.origin - vectorScale(ileri, 260);
	level.player allowProne(false);
	level.player allowCrouch(false);
	org = spawn("script_origin", level.player.origin);
	org.angles = level.player getplayerangles();
	level.player playerlinktoabsolute(org);
	org moveto((arka[0], arka[1], level.player.origin[2]), 0.5, 0.1, 0.2);
	org rotateto((10, k.angles[1] + 180, 0), 0.5);
	wait 0.55;
	ust = k gettagorigin("tag_player");
	org moveto((arka[0], arka[1], ust[2]), 0.6, 0.2, 0.2);
	wait 0.65;
	org moveto(ust, 0.7, 0.2, 0.3);
	org rotateto((5, k.angles[1] + 180, 0), 0.7);
	wait 0.75;
	level.player unlink();
	org delete();
	level.player setplayerangles((5, k.angles[1] + 180, 0));
	level.player playerLinkToDelta(k, "tag_player", 1);
	test_yaz("oyuncu kasada");
}

// stok germantruck buddyjump: tag_climbnode'a bagli climbin (sirayla), sonra kasada ayakta
kasaya_bin(k, i)
{
	self endon("death");
	an = level.kr_anim["kasa_tirman"][i % 2];
	for (w = 0; w < 200 && level.kasaya_binen < i; w++)
	{
		cn = k gettagorigin("tag_climbnode");
		ca = k gettagangles("tag_climbnode");
		self setgoalpos(getstartorigin(cn, ca, an) - vectorScale(anglestoforward(ca), 60));
		wait 0.25;
	}
	cn = k gettagorigin("tag_climbnode");
	ca = k gettagangles("tag_climbnode");
	bas = getstartorigin(cn, ca, an);
	self.goalradius = 16;
	for (w = 0; w < 60 && distance(self.origin, bas) > 40; w++)
	{
		self setgoalpos(bas);
		wait 0.25;
	}
	self.allowdeath = 0;
	self linkto(k, "tag_climbnode", (0, 0, 0), (0, 0, 0));
	self animscripted("kasaya_bin", cn, ca, an);
	self waittillmatch("kasaya_bin", "end");
	tag = "tag_guy0" + (1 + i);
	self unlink();
	self linkto(k, tag, (0, 0, 0), (0, 0, 0));
	level.kasaya_binen++;
	for (;;)
	{
		self animscripted("kasada", k gettagorigin(tag), k gettagangles(tag), level.kr_anim["kasa_bekle"]);
		self waittillmatch("kasada", "end");
	}
}

tetik_kapat_ent()
{
	self.eski_yer = self.origin;
	self.origin = self.origin + (0, 0, 0 - 10000);
}

tetik_ac()
{
	self.origin = self.eski_yer;
}

// --------------------------------------------------------------------------
// YARDIMCILAR
// --------------------------------------------------------------------------
canli_say(liste)
{
	n = 0;
	if (!isdefined(liste))
		return 0;
	for (i = 0; i < liste.size; i++)
		if (isalive(liste[i]))
			n++;
	return n;
}

siper_onbellek()
{
	level.siper = [];
	nodes = getallnodes();
	for (i = 0; i < nodes.size; i++)
		if (issubstr(nodes[i].type, "Cover"))
			level.siper[level.siper.size] = nodes[i];
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

hedef_bekle(sure)
{
	self endon("goal");
	wait sure;
}

zemin_bul(nokta)
{
	tr = bulletTrace(nokta + (0, 0, 400), nokta - (0, 0, 800), false, undefined);
	return tr["position"] + (0, 0, 4);
}

bolum_sonu(sure)
{
	perde = newHudElem();
	perde.x = 0;
	perde.y = 0;
	perde.horzAlign = "fullscreen";
	perde.vertAlign = "fullscreen";
	perde.foreground = true;
	perde.alpha = 0;
	perde setshader("black", 640, 480);
	perde fadeOverTime(sure);
	perde.alpha = 1;
	wait sure + 0.5;
	test_yaz("GOREV TAMAM");
	missionSuccess("credits", false);             // bagimsiz bolum: jenerik
}

price_der(replik)
{
	if (!isdefined(level.price) || !isalive(level.price))
		return;
	if (!isdefined(level.replik_no))
		level.replik_no = 0;
	level.replik_no++;
	no = level.replik_no;
	level thread price_soyle(replik, no);
	for (t = 0; t < 110; t++)
	{
		if (isdefined(level.replik_bitti) && level.replik_bitti >= no)
			return;
		wait 0.1;
	}
}

price_soyle(replik, no)
{
	g = level.price;
	if (isalive(g))
	{
		g setBattleChatter(false);
		ses_cal(g, "sidirezegh_price_" + replik, 11);
		if (isalive(g))
			g setBattleChatter(true);
	}
	level.replik_bitti = no;
}

ses_cal(kim, alias, sure)
{
	org = spawn("script_origin", kim.origin + (0, 0, 60));
	org linkto(kim);
	org playsound(alias, "ses_bitti");
	org bekle_ya(sure, "ses_bitti");
	org delete();
}

bekle_ya(sure, a)
{
	self endon(a);
	wait sure;
}

asker_der(ad)
{
	konusan = undefined;
	for (i = 0; i < level.ekip.size; i++)
		if (isalive(level.ekip[i]) && (!isdefined(level.price) || level.ekip[i] != level.price))
		{
			konusan = level.ekip[i];
			break;
		}
	if (!isdefined(konusan))
		konusan = level.player;
	ses_cal(konusan, "sidirezegh_asker_" + ad, 6);
}

muzik(alias)
{
	level notify("muzik_degisti");
	level endon("muzik_degisti");
	musicstop(2);
	wait 2.1;
	musicplay(alias);
}

muzik_bir(alias)
{
	level notify("muzik_degisti");
	musicstop(1);
	wait 1.1;
	musicplay(alias);
}

// oyuncu kasabadan (meydan karesi) cikmaz
sinir_bekcisi()
{
	level endon("sinir_kalk");
	son = level.player.origin;
	disari = 0;
	for (;;)
	{
		p = level.player.origin;
		if (cokgen_icinde(p, level.kare))
		{
			son = p;
			disari = 0;
		}
		else
		{
			disari++;
			if (disari > 20)
			{
				level.player setorigin(son);
				disari = 0;
			}
		}
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

test_yaz(msg)
{
	setcvar("kr_log", msg);
}

test_olumsuz()
{
	for (;;)
	{
		level.player.maxhealth = 100000;
		level.player.health = 100000;
		wait 0.05;
	}
}

// --------------------------------------------------------------------------
// GOREV AKISI TESTI (kr_tur 2): otomatik oyuncu, asamalari kr_log / kr_durum ile yazar
// --------------------------------------------------------------------------
akis_testi()
{
	level thread test_olumsuz();
	level thread akis_izle();
	wait 2;
	for (;;)
	{
		ai = getaiarray("axis");
		if (ai.size && level.asama != "BASLANGIC")
		{
			k = ai[randomint(ai.size)];
			k dodamage(k.health + 500, k.origin);
		}
		if (isdefined(level.schreck) && !level.player hasweapon("panzerschreck"))
		{
			level.player setorigin(zemin_bul(level.schreck.origin + (0, 0 - 60, 0)));
			wait 1;
			level.player takeWeapon("thompson");
			level.player giveWeapon("panzerschreck");
			test_yaz("panzerschreck alindi");
		}
		if (level.player hasweapon("panzerschreck") && isdefined(level.panzer) && isdefined(level.panzer.durdu) && !flag("panzer_oldu"))
		{
			wait 3;
			level.panzer notify("ates_dur");
			level.panzer dodamage(50000, level.panzer.origin);
			level.panzer notify("death");
			flag_set("panzer_oldu");
			test_yaz("panzer yok edildi (test)");
		}
		if (level.asama == "BIN" && isdefined(level.kamyon_tetik))
		{
			wait 2;
			if (isdefined(level.kamyon_tetik))
				level.kamyon_tetik notify("trigger", level.player);
		}
		wait 1.5;
	}
}

akis_izle()
{
	son = "";
	for (;;)
	{
		if (level.asama != son)
		{
			son = level.asama;
			test_yaz("ASAMA " + son);
		}
		dg = "-";
		if (isdefined(level.dalga_dogan))
			dg = "" + level.dalga_dogan + "/" + level.dalga_hedef;
		setcvar("kr_durum", son + " ai=" + getaiarray().size + " axis=" + getaiarray("axis").size
			+ " ekip=" + canli_say(level.ekip) + " dalga=" + dg + " canli=" + canli_say(level.dalga_ai));
		wait 15;
	}
}

// --------------------------------------------------------------------------
// EKRAN TURU (kr_tur 1): gorsel kalite kontrolu
// --------------------------------------------------------------------------
ekran_turu()
{
	level.player takeallweapons();
	level thread test_olumsuz();
	y = getent("panzerschreck_yer", "targetname");
	s = spawn("weapon_panzerschreck", y.origin, 1);
	s.angles = (-74, 90, 0);
	n = [];
	a = [];
	n[n.size] = (0, 0, 4200);         a[a.size] = (89, 90, 0);    // 1 kasaba ustten
	n[n.size] = (0, -1100, 260);      a[a.size] = (8, 90, 0);     // 2 karargah on cephe (meydan)
	n[n.size] = (1100, 1100, 500);    a[a.size] = (20, 225, 0);   // 3 meydan KD'den
	n[n.size] = (-1100, -1100, 500);  a[a.size] = (20, 45, 0);    // 4 meydan GB'den
	n[n.size] = (60, -100, 110);      a[a.size] = (4, 90, 0);     // 5 zemin kat ici (kuzey duvar, panzerschreck)
	n[n.size] = (-120, 120, 110);     a[a.size] = (25, 90, 0);    // 6 panzerschreck yakin
	n[n.size] = (-120, -210, 110);    a[a.size] = (15, 120, 0);   // 7 merdiven alttan
	n[n.size] = (60, 0, 250);         a[a.size] = (4, 270, 0);    // 8 ust kat -> guney pencereler
	n[n.size] = (-170, 130, 250);     a[a.size] = (40, 250, 0);   // 9 merdiven ustten
	n[n.size] = (60, 0, 250);         a[a.size] = (4, 90, 0);     // 10 ust kat -> kuzey
	n[n.size] = (0, 1400, 160);       a[a.size] = (4, 90, 0);     // 11 kuzey sokak agzi -> disari
	n[n.size] = (1400, 0, 160);       a[a.size] = (4, 0, 0);      // 12 dogu agzi -> disari
	n[n.size] = (0, -1400, 160);      a[a.size] = (4, 270, 0);    // 13 guney agzi -> disari (Panzer)
	n[n.size] = (-1400, 0, 160);      a[a.size] = (4, 180, 0);    // 14 bati agzi -> disari (takviye)
	n[n.size] = (0, 2600, 500);       a[a.size] = (8, 270, 0);    // 15 kuzeyden kasabaya
	n[n.size] = (2600, 0, 500);       a[a.size] = (8, 180, 0);    // 16 doguda kasabaya
	n[n.size] = (0, -2600, 500);      a[a.size] = (8, 90, 0);     // 17 guneyden kasabaya
	n[n.size] = (-2600, 0, 500);      a[a.size] = (8, 0, 0);      // 18 batidan kasabaya
	n[n.size] = (-900, 1200, 200);    a[a.size] = (5, 315, 0);    // 19 KB bina + pazar
	n[n.size] = (900, -1200, 200);    a[a.size] = (5, 135, 0);    // 20 GD bina
	n[n.size] = (3800, 3800, 900);    a[a.size] = (12, 225, 0);   // 21 ufuk KD
	n[n.size] = (-3800, -3800, 900);  a[a.size] = (12, 45, 0);    // 22 ufuk GB
	setcvar("kr_adim", "0");
	wait 3;
	for (i = 0; i < n.size; i++)
	{
		setcvar("kr_adim", "" + (i + 1));
		for (t = 0; t < 200; t++)
		{
			level.player setorigin(n[i]);
			level.player setplayerangles(a[i]);
			wait 0.05;
		}
	}
	setcvar("kr_adim", "bitti");
}

// kullanici: ayni yerde iki asker siper almasin -- ust uste binen ikiliden biri bos pencereye
siper_denetci()
{
	for (;;)
	{
		wait 2;
		if (level.ekip_mod == "sahne")
			return;
		t = tum_ingilizler();
		for (i = 0; i < t.size; i++)
			for (j = i + 1; j < t.size; j++)
				if (isalive(t[i]) && isalive(t[j]) && distance(t[i].origin, t[j].origin) < 36)
				{
					g = t[j];
					if (g == level.price)
						g = t[i];
					g yer_degistir();
				}
	}
}

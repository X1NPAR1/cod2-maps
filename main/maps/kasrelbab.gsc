// kasrelbab.gsc -- "Operation Silent Dawn", Kasr el-Bab, Misir, 2 Kasim 1942, safak (kumtepe'nin devami).
//
// AKIS (kullanici kararlari):
//   1) GIZLEN: oyuncu tepedeki calilarda; Alman konvoyu (2 Blitz, yari paletli, Panzer II)
//      asagidaki yoldan gecer. Bir arac 1500'den yakinken oyuncu yatmiyorsa ya da calidan
//      ciktiysa TESPIT: araclar durur, ates acilir, oyuncu olur.
//   2) KULUBE: konvoy gidince 2 Alman (nobet + telsizci) susturulur; telsiz F ile.
//   3) TAKVIYE: ~40 sn sonra gizli vadiden 5 Crusader + 20 Ingiliz + Price (olumsuz).
//   4) BASKIN: Crusaderlar sur MG'lerini ve buyuk kapiyi vurur; kasabada 25 Alman.
//   5) FLAK: 3 flak88 (3'er murettebat) ates eder; F ile patlayici, 5 sn.
//   6) PANZER: son flak patlayinca cikis yolundan Panzer II; arkasina TNT (F), 5 sn.
//   7) CIKIS: kapidaki kamyon; Price + 3 asker; F ile kasaya bin; Price konusur; bir
//      asker kamyonun onune yururken kararma -> jenerik.
// Kaliplar: kumtepe (gorunmez dogus, pencere siperleri, tank atisi, yikim, ses), beltot
// (tag_player), burya (TNT + sayac), decoytown/stok _flak88 (flak).
#include maps\_utility;
#include maps\_anim;

main()
{
	setExpFog(0.00015, .86, .72, .62, 0);          // kullanici: sis hafifletildi
	setCullDist(20000);

	precacheString(&"KASRELBAB_OBJ_GIZLEN");
	precacheString(&"KASRELBAB_OBJ_KULUBE");
	precacheString(&"KASRELBAB_OBJ_TELSIZ");
	precacheString(&"KASRELBAB_OBJ_TOPLAN");
	precacheString(&"KASRELBAB_OBJ_KASABA");
	precacheString(&"KASRELBAB_OBJ_FLAK");
	precacheString(&"KASRELBAB_OBJ_PANZER");
	precacheString(&"KASRELBAB_OBJ_KAMYON");
	precacheString(&"KASRELBAB_MSG_TESPIT");
	precacheString(&"KASRELBAB_MSG_YAT");
	precacheString(&"KASRELBAB_INTRO_TITLE");
	precacheString(&"KASRELBAB_INTRO_PLACE");
	precacheString(&"KASRELBAB_INTRO_DATE");
	precacheString(&"KASRELBAB_INTRO_INFO");
	precacheString(&"KASRELBAB_PLATFORM_TELSIZ");
	precacheString(&"KASRELBAB_PLATFORM_PATLAYICI");
	precacheString(&"KASRELBAB_PLATFORM_KAMYON");
	precacheShader("black");
	precacheShader("hudStopwatch");
	precacheShader("hudStopwatchNeedle");
	precacheModel("xmodel/military_german_fieldradio_green");
	precacheModel("xmodel/military_german_fieldradio_green_obj");
	precacheModel("xmodel/military_tntbomb");
	precacheModel("xmodel/military_tntbomb_obj");
	precacheModel("xmodel/german_artillery_flak88_aa_d_static");
	precacheModel("xmodel/weapon_stickybomb");
	precacheModel("xmodel/weapon_stickybomb_obj");
	precacheModel("xmodel/egypt_prop_buildingpiece01");
	precacheModel("xmodel/egypt_prop_buildingpiece02");
	precacheModel("xmodel/egypt_prop_buildingpiece03");

	level.campaign = "british";
	level.totalfriends = 0;
	level.maxfriendlies = 0;
	maps\_truck::main("xmodel/vehicle_opel_blitz_desert");
	maps\_crusader::main("xmodel/vehicle_crusader2");
	maps\_panzer2::main("xmodel/vehicle_panzer_ii");
	maps\_halftrack::main("xmodel/vehicle_halftrack_mg_desert");
	maps\kasrelbab_fx::main();
	maps\_load::main();
	maps\kasrelbab_anim::main();

	level.ekip_mod = "bekle";
	level.hucum_siper = [];
	flag_init("kalk");
	flag_init("tanitim_bitti");
	flag_init("tespit");
	flag_init("konvoy_gecti");
	flag_init("bitti");
	flag_init("takviye_geldi");
	flag_init("kapi_kirildi");

	level.sinir = maps\kasrelbab_sinir::cokgen();
	level.cali = getent("cali", "targetname").origin;
	level.kulube = getent("kulube_m", "targetname").origin;
	level.meydan = getent("kasaba_meydan", "targetname").origin;
	level.kapi_m = getent("buyuk_kapi_m", "targetname").origin;
	level.cikis_m = getent("cikis_kapi_m", "targetname").origin;
	level.asama = "BASLANGIC";
	// buyuk kapi: gok kutusu icinde derlendi, yerine konur; enkazi gizli
	level.kapi = getentarray("buyuk_kapi", "targetname");
	for (i = 0; i < level.kapi.size; i++)
		level.kapi[i] moveto(level.kapi[i].origin + (6656, 0, 0 - 2048), 0.05);
	tetik_kapat("telsiz_tetik");
	tetik_kapat("kamyon_bin");
	t = getentarray("flak_tetik", "targetname");
	for (i = 0; i < t.size; i++)
		t[i] tetik_kapat_ent();
	tetik_kapat("panzer_tetik");

	if (getcvar("kr_tur") == "2")
		level thread akis_testi();
	else if (getcvar("kr_tur") != "" && getcvar("kr_tur") != "0")
	{
		level thread ekran_turu();
		return;
	}
	oyuncu_techizat();
	siper_onbellek();
	anim.noWeaponToss = true;
	level.ekip = [];
	level thread ekip_beyni();
	level thread flaklar_ates();
	level thread gorevler();
}

tetik_kapat(ad)
{
	getent(ad, "targetname") tetik_kapat_ent();
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
tanitim()
{
	level.introblack = newHudElem();
	level.introblack.x = 0;
	level.introblack.y = 0;
	level.introblack.horzAlign = "fullscreen";
	level.introblack.vertAlign = "fullscreen";
	level.introblack.foreground = true;
	level.introblack setShader("black", 640, 480);
	musicplay("kasrelbab_muzik_giris");
	wait .05;
	level.introstring = [];
	maps\_introscreen::introscreen_create_line(&"KASRELBAB_INTRO_TITLE");
	wait 2;
	maps\_introscreen::introscreen_create_line(&"KASRELBAB_INTRO_PLACE");
	maps\_introscreen::introscreen_create_line(&"KASRELBAB_INTRO_DATE");
	wait 2;
	maps\_introscreen::introscreen_create_line(&"KASRELBAB_INTRO_INFO");
	wait 3;
	level.introblack fadeOverTime(3);
	level.introblack.alpha = 0;
	maps\_introscreen::introscreen_fadeOutText();
	flag_set("tanitim_bitti");
}

// kullanici: Lee-Enfield + Sten, 4 el bombasi, 2 duman
oyuncu_techizat()
{
	level.player takeallweapons();
	level.player giveWeapon("enfield");
	level.player giveWeapon("sten");
	level.player giveWeapon("MK1britishfrag");
	level.player giveWeapon("smoke_grenade_american");
	level.player giveMaxAmmo("enfield");
	level.player giveMaxAmmo("sten");
	level.player setWeaponClipAmmo("MK1britishfrag", 4);
	level.player setWeaponClipAmmo("smoke_grenade_american", 2);
	level.player switchToWeapon("enfield");
	level.player switchToOffhand("MK1britishfrag");
	maps\_loadout::setup_british_africa();
}

// --------------------------------------------------------------------------
// GOREV AKISI
// --------------------------------------------------------------------------
gorevler()
{
	level thread tanitim();
	level thread sinir_bekcisi();

	// --- 1) GIZLEN: konvoy gecer
	level.asama = "GIZLEN";
	objective_add(1, "active", &"KASRELBAB_OBJ_GIZLEN", level.cali);
	objective_current(1);
	level thread muzik("kasrelbab_muzik_gizlen");
	flag_wait("tanitim_bitti");
	level thread autoSaveByName("gizlen");
	ses_cal(level.player, "kasrelbab_price_gizlen", 4);       // (telsiz) Gizlenin!
	konvoy();
	objective_state(1, "done");
	level thread autoSaveByName("konvoy_gecti");

	// --- 2) KULUBE: tek Alman, telsize donuk
	level.asama = "KULUBE";
	objective_add(2, "active", &"KASRELBAB_OBJ_KULUBE", level.kulube);
	objective_current(2);
	k = kulube_alman();
	while (isalive(k))
		wait 0.3;
	objective_state(2, "done");

	// --- 3) TELSIZ
	level.asama = "TELSIZ";
	r = getent("telsiz", "targetname");
	objective_add(3, "active", &"KASRELBAB_OBJ_TELSIZ", r.origin);
	objective_current(3);
	r thread telsiz_yanip_son();
	telsiz_kullan();
	objective_state(3, "done");
	level thread autoSaveByName("telsiz");

	// --- 4) TAKVIYE: 20 sn sonra Price + 12; 5 sn sonra Crusaderlar
	level.asama = "TAKVIYE";
	wait 20;
	ingilizler_gelir();
	wait 5;
	level thread crusaderlar_gelir();
	objective_add(4, "active", &"KASRELBAB_OBJ_TOPLAN", level.price.origin);
	objective_current(4);
	level thread price_obj(4);
	for (t = 0; t < 400; t++)
	{
		if (distance(level.price.origin, level.kulube) < 700 && distance(level.player.origin, level.price.origin) < 300)
			break;
		price_yetistir();                             // kullanici: Price hep gec geliyordu
		wait 0.5;
	}
	level notify("price_obj_dur");
	objective_state(4, "done");
	price_der("brifing");

	// --- 5) BASKIN: herkes kapinin onune; oyuncu yaklasinca Crusader kapiyi devirir
	level.asama = "BASKIN";
	objective_add(5, "active", &"KASRELBAB_OBJ_KASABA", level.kapi_m);
	objective_current(5);
	level thread muzik("kasrelbab_muzik_baskin");
	level.ekip_mod = "sahne";
	ekip_noktaya(level.kapi_m + (0 - 820, 0, 0), 380, 300);   // kullanici: brifingden sonra herkes Crusaderlarin yanina
	level thread price_der("hucum");
	while (distance(level.player.origin, level.kapi_m) > 950)
		wait 0.3;
	level.kasaba_ai = [];
	level thread kasaba_dogus(32);
	level thread sur_mgleri();
	crusader_kapi();
	ekip_noktaya(level.meydan + (0 - 500, 0, 0), 300, 700);   // kapi devrilince herkes iceri dalar
	level thread ekip_hucum_gecikmeli(level.meydan, 1300, 9);
	level thread kasabaya_kapat();
	level thread price_der("git");
	wait 10;
	while (level.kasaba_kalan > 4)
		wait 1;
	objective_state(5, "done");
	level thread autoSaveByName("kasaba");
	level.ekip_mod = "bekle";
	for (i = 0; i < level.ekip.size; i++)
		if (isalive(level.ekip[i]))
			level.ekip[i] thread bolge_dolas(level.meydan, 1100, -9999, 9999);   // ara sira siper degistirir

	// --- 6) FLAKLAR
	level.asama = "FLAK";
	level thread muzik("kasrelbab_muzik_flak");
	price_der("flak");
	f = getentarray("flak", "targetname");
	objective_add(6, "active", &"KASRELBAB_OBJ_FLAK", f[0].origin);
	for (i = 1; i < f.size; i++)
		objective_additionalposition(6, i, f[i].origin);
	objective_current(6);
	level.flak_biten = 0;
	for (i = 0; i < f.size; i++)
		f[i] thread flak_gorevi(i);
	objective_additionalposition(6, 0, f[0].origin);
	while (level.flak_biten < f.size)
		wait 0.5;
	objective_state(6, "done");
	price_der("flak_bitti");
	level thread autoSaveByName("flak");

	// --- 7) PANZER
	level.asama = "PANZER";
	dogu_saldirisi();                                 // kullanici: Panzer'den once 10 Alman dogudan saldirir
	panzer_son();
	level thread autoSaveByName("panzer");

	// --- 8) CIKIS: kamyon
	level.asama = "CIKIS";
	kamyon_cikis();
}

flag_wait_t(ad, sure)
{
	for (t = 0; t < sure * 10 && !flag(ad); t++)
		wait 0.1;
}

// --------------------------------------------------------------------------
// 1) KONVOY ve TESPIT (kullanici: yatmazsan / calidan cikarsan olursun)
// --------------------------------------------------------------------------
konvoy()
{
	level.player.ignoreme = true;                     // tespit edilmedikce kimse oyuncuyu hedeflemez
	level.konvoy = [];
	for (g = 1; g <= 4; g++)
	{
		if (g <= 3)
			arac_yolcu_hazirla(g, "konvoy" + g, 28);
		a = maps\_vehicle::scripted_spawn(g);
		v = a[0];
		level.konvoy[level.konvoy.size] = v;
		v thread arac_olumsuz();
		if (isdefined(v.mgturret))
			for (m = 0; m < v.mgturret.size; m++)
				v.mgturret[m] setmode("manual");
		v.yolcular = [];
		if (isdefined(v.riders))
			for (i = 0; i < v.riders.size; i++)
				if (isalive(v.riders[i]))
				{
					v.riders[i].ignoreall = true;
					v.riders[i].ignoreme = true;
					v.yolcular[v.yolcular.size] = v.riders[i];
				}
	}
	level thread tespit_bekcisi();
	for (g = 0; g < level.konvoy.size; g++)
	{
		level thread maps\_vehicle::gopath(level.konvoy[g]);
		level.konvoy[g] thread konvoy_sonu();
		if (g == 1)
			iprintlnbold(&"KASRELBAB_MSG_YAT");
		wait 6;
	}
	son = getent("konvoy_son", "targetname").origin;
	for (;;)
	{
		if (flag("tespit"))
			level waittill("sonsuz");
		n = 0;
		for (g = 0; g < 2; g++)
			if (!isdefined(level.konvoy[g]) || distance(level.konvoy[g].origin, son) < 450 || isdefined(level.konvoy[g].gecti))
				n++;
		if (n >= 2)
			break;
		wait 0.3;
	}
	flag_set("konvoy_gecti");
	level.player.ignoreme = false;
}

// arac viewpos(2)'yi gecince, gorunmeden yolcularla birlikte silinir (yolda yolcu kalmaz)
konvoy_sonu()
{
	self endon("death");
	son = getent("konvoy_son", "targetname").origin;
	while (distance(self.origin, son) > 450)
		wait 0.2;
	self.gecti = true;
	// kullanici: yolun sonuna gidip kaybolsun; sondaki indirmeden ONCE silinir (yolcular saldiriyordu)
	son2 = (0 - 400, 0 - 7900, 0);
	while (distance((self.origin[0], self.origin[1], 0), son2) > 900)
		wait 0.2;
	if (isdefined(self.yolcular))
		for (i = 0; i < self.yolcular.size; i++)
			if (isdefined(self.yolcular[i]))
				self.yolcular[i] delete();
	if (isdefined(self.riders))
		for (i = 0; i < self.riders.size; i++)
			if (isdefined(self.riders[i]))
				self.riders[i] delete();
	self notify("olumsuz_bitti");
	self delete();
}

tespit_bekcisi()
{
	level endon("konvoy_gecti");
	for (;;)
	{
		wait 0.2;
		yakin = false;
		for (i = 0; i < level.konvoy.size; i++)
			if (isdefined(level.konvoy[i]) && distance(level.konvoy[i].origin, level.player.origin) < 1500)
				yakin = true;
		if (!yakin)
			continue;
		calida = distance((level.player.origin[0], level.player.origin[1], 0), (level.cali[0], level.cali[1], 0)) < 260;
		if (level.player getstance() != "prone" || !calida)
		{
			level thread tespit_edildi();
			return;
		}
	}
}

tespit_edildi()
{
	flag_set("tespit");
	level.player.ignoreme = false;
	iprintlnbold(&"KASRELBAB_MSG_TESPIT");
	for (i = 0; i < level.konvoy.size; i++)
	{
		v = level.konvoy[i];
		v setspeed(0, 15);
		v notify("unload");
		if (i >= 2)                                 // yari paletli MG ve Panzer topu
		{
			if (i == 3)
				v setturrettargetent(level.player, (0, 0, 32));
			v thread tespit_ates(i == 3);
		}
	}
	wait 1.5;
	ai = getaiarray("axis");
	for (i = 0; i < ai.size; i++)
	{
		ai[i].ignoreall = false;
		ai[i].favoriteenemy = level.player;
		ai[i] setgoalpos(level.player.origin);
	}
	wait 2.5;
	level.player enableHealthShield(false);
	for (t = 0; t < 20 && isalive(level.player); t++)
	{
		radiusDamage(level.player.origin + (0, 0, 20), 120, 60, 40);
		playfx(level._effect["tank_patlama"], level.player.origin + (randomfloatrange(-150, 150), randomfloatrange(-150, 150), 0));
		wait 0.6;
	}
}

tespit_ates(top)
{
	self endon("death");
	for (;;)
	{
		if (top)
			self notify("turret_fire");
		if (isdefined(self.mgturret) && isdefined(self.mgturret[0]))
		{
			self.mgturret[0] setmode("auto_nonai");
			self.mgturret[0] setturretteam("axis");
		}
		wait 2;
	}
}

// --------------------------------------------------------------------------
// 2) KULUBE: tek Alman telsize donuk (sirti kapiya); vurulunca ya da cok yaklasinca tepki
kulube_alman()
{
	sp = getentarray("kulube_alman", "targetname");
	g = dogur(sp[0]);
	sp[0] delete();
	g.ignoreall = true;
	g.goalradius = 4;
	g setgoalpos(g.origin);
	g allowedstances("stand");
	g thread kulube_tepki();
	return g;
}

kulube_tepki()
{
	self endon("death");
	while (distance(level.player.origin, self.origin) > 110)
	{
		self.health = 100;
		wait 0.2;
		if (self.health < 100)
			break;
	}
	self.ignoreall = false;
}

ingilizler_gelir()
{
	sp = getentarray("price", "targetname");
	level.price = dogur(sp[0]);
	sp[0] delete();
	level.price.animname = "price";
	level.price thread magic_bullet_shield();
	level.price.dontavoidplayer = true;
	level.ekip[level.ekip.size] = level.price;
	level.price thread takilma_bekcisi();
	sp = getentarray("ingiliz", "targetname");
	for (i = 0; i < sp.size; i++)
	{
		g = dogur(sp[i]);
		sp[i] delete();
		if (!isdefined(g))
			continue;
		g.health = 1450;
		g.maxhealth = 1450;
		level.ekip[level.ekip.size] = g;
		g thread geride_kalma();
		if (!isdefined(level.kamyon_ikili))
			level.kamyon_ikili = [];
		if (level.kamyon_ikili.size < 2)
		{
			g thread magic_bullet_shield();            // finalde kasaya binecek iki asker
			level.kamyon_ikili[level.kamyon_ikili.size] = g;
		}
		wait 0.1;
	}
	// Price kendi dogus noktasinda donup kaliyordu (olculdu: diger 12 kosarken yerinden kipirdamadi);
	// oyuncu cok uzakta/gormuyor -> askerlerin arasina alinir
	if (level.ekip.size > 2 && distance(level.player.origin, level.price.origin) > 2500)
		level.price teleport(zemin_bul(level.ekip[2].origin + (0, 70, 0)));
	t = getent("toplanma", "targetname").origin;
	for (i = 0; i < level.ekip.size; i++)
	{
		level.ekip[i].walkdist = 0;                 // kullanici: Price yurudugu icin cok gec geliyordu -> kossunlar
		a = 360.0 * i / level.ekip.size;
		level.ekip[i].goalradius = 48;
		// kullanici: Price hic kipirdamadi -- serbest noktaya rota bulamayan AI durur -> en yakin GERCEK yol dugumu
		n = yakin_dugum(t + (cos(a) * (160 + (i % 3) * 70), sin(a) * (160 + (i % 3) * 70), 0));
		level.ekip[i].hedef_yer = n.origin;
		level.ekip[i] setgoalnode(n);
	}
}

price_obj(no)
{
	level endon("price_obj_dur");
	for (;;)
	{
		if (isalive(level.price))
			objective_position(no, level.price.origin);
		wait 0.5;
	}
}

crusaderlar_gelir()
{
	level.crusader = [];
	for (k = 0; k < 5; k++)
	{
		a = maps\_vehicle::scripted_spawn(5 + k);
		c = a[0];
		c thread arac_olumsuz();
		c thread crusader_durak("crusader" + (k + 1) + "_durak");
		level.crusader[k] = c;
		level thread arac_yola(c, k * 2.6);
		wait 1.25;
	}
	level thread asker_der("zebra");
}

// oyuncu kapiya yaklasinca: Crusader sur MG'lerini, sonra kapiyi vurur; kanatlar disa devrilir
crusader_kapi()
{
	for (t = 0; t < 60; t++)
	{
		n = 0;
		for (k = 0; k < level.crusader.size; k++)
			if (isdefined(level.crusader[k]) && isdefined(level.crusader[k].durdu))
				n++;
		if (n >= 2)
			break;
		wait 0.5;
	}
	c = level.crusader[2];
	mg = getentarray("sur_mg", "targetname");
	for (i = 0; i < mg.size; i++)
	{
		c tank_vur(mg[i]);
		patlama(mg[i].origin);
		o = mg[i].origin;
		ai = getaiarray("axis");
		for (k = 0; k < ai.size; k++)
			if (distance(ai[k].origin, o) < 220)
				ai[k] dodamage(ai[k].health + 500, o);
		mg[i] thread mg_kaldir();
		// (duman kaldirildi: kullanici cok fazla dedi)
		wait 1.5;
	}
	h = spawn("script_origin", level.kapi_m);
	c tank_vur(h);
	patlama(level.kapi_m);
	for (i = 0; i < level.kapi.size; i++)
	{
		level.kapi[i] notsolid();
		level.kapi[i] rotatepitch(0 - 90, 1.1, 0.8, 0);      // disa dogru yere yatar
		level.kapi[i] movez(0 - 14, 1.1, 0.8, 0);            // kullanici: biraz daha asagi
	}
	parca_sac(level.kapi_m, 6);
	playfx(level._effect["bina_toz"], level.kapi_m - (150, 0, 100));
	wait 1.2;
	earthquake(0.4, 0.8, level.kapi_m, 1500);
	playfx(level._effect["bina_toz"], level.kapi_m - (250, 0, 110));
	h delete();
	flag_set("kapi_kirildi");
}

// kasaba: once 12 + flak murettebati 9; olen yerine gorunmeden yenisi (toplam adet)
kasaba_dogus(toplam)
{
	sp = getentarray("kasaba", "targetname");
	level.kasaba_kalan = toplam;
	f = getentarray("flak", "targetname");
	mur = getentarray("flak_murettebat", "targetname");
	for (i = 0; i < f.size; i++)
	{
		f[i].murettebat = [];
		for (k = 0; k < mur.size; k++)
			if (isdefined(mur[k]) && isdefined(mur[k].script_noteworthy) && mur[k].script_noteworthy == f[i].script_noteworthy)
			{
				g = dogur(mur[k]);
				mur[k] delete();
				if (isdefined(g))
				{
					f[i].murettebat[f[i].murettebat.size] = g;
					g.flakci = true;
					g thread bolge_dolas(f[i].origin, 320, -9999, 9999);
				}
			}
	}
	dogan = 0;
	sira = 0;
	ai = [];
	while (dogan < toplam)
	{
		while (canli_say(ai) >= 12 || getaiarray().size >= 31)
			wait 0.5;
		s_ = sp[sira % sp.size];
		sira++;                                       // gorunen/basarisiz spawner atlanir, siradaki denenir
		if (dogan >= 12 && gorunur(s_.origin + (0, 0, 40)))
		{
			wait 0.2;
			continue;
		}
		if (dogan >= 12)
			wait randomfloatrange(1, 3);
		g = dogur(s_);
		if (!isdefined(g))
			continue;
		ai[ai.size] = g;
		level.kasaba_ai = ai;
		dogan++;
		g thread bolge_dolas(g.origin, 500, -9999, 9999);
		g thread kasaba_say();
	}
}

kasaba_say()
{
	self waittill("death");
	level.kasaba_kalan--;
}

// --------------------------------------------------------------------------
// 3) TELSIZ
// --------------------------------------------------------------------------
telsiz_kullan()
{
	r = getent("telsiz", "targetname");
	t = getent("telsiz_tetik", "targetname");
	t tetik_ac();
	t sethintstring(&"KASRELBAB_PLATFORM_TELSIZ");
	t waittill("trigger");
	r notify("kullanildi");
	r setmodel("xmodel/military_german_fieldradio_green");
	t delete();
	ses_cal(level.player, "kasrelbab_asker_telsiz", 10);
	ses_cal(r, "kasrelbab_asker_cevap", 9);
}

telsiz_yanip_son()
{
	self endon("kullanildi");
	for (;;)
	{
		self setmodel("xmodel/military_german_fieldradio_green_obj");
		wait 0.5;
		self setmodel("xmodel/military_german_fieldradio_green");
		wait 0.35;
	}
}

// --------------------------------------------------------------------------
// 4) TAKVIYE: Crusaderlar (1.25 sn arayla dogar, 2.6 sn arayla yola cikar) + piyade + Price
// --------------------------------------------------------------------------
takviye_gelir()
{
	level.crusader = [];
	for (k = 0; k < 5; k++)
	{
		a = maps\_vehicle::scripted_spawn(5 + k);
		c = a[0];
		c thread arac_olumsuz();
		c thread crusader_durak("crusader" + (k + 1) + "_durak");
		level.crusader[k] = c;
		level thread arac_yola(c, k * 2.6);
		wait 1.25;
	}
	level thread asker_der("zebra");
	sp = getentarray("price", "targetname");
	level.price = dogur(sp[0]);
	sp[0] delete();
	level.price.animname = "price";
	level.price thread magic_bullet_shield();
	level.price.dontavoidplayer = true;
	level.price.ekip_uyesi = true;
	level.ekip[level.ekip.size] = level.price;
	sp = getentarray("ingiliz", "targetname");
	for (i = 0; i < sp.size; i++)
	{
		g = dogur(sp[i]);
		sp[i] delete();
		if (!isdefined(g))
			continue;
		g.health = 1450;
		g.maxhealth = 1450;
		g.ekip_uyesi = true;
		level.ekip[level.ekip.size] = g;
		wait 0.15;
	}
	// kulube onunde toplanma
	// Price kendi dogus noktasinda donup kaliyordu (olculdu: diger 12 kosarken yerinden kipirdamadi);
	// oyuncu cok uzakta/gormuyor -> askerlerin arasina alinir
	if (level.ekip.size > 2 && distance(level.player.origin, level.price.origin) > 2500)
		level.price teleport(zemin_bul(level.ekip[2].origin + (0, 70, 0)));
	t = getent("toplanma", "targetname").origin;
	for (i = 0; i < level.ekip.size; i++)
	{
		level.ekip[i].walkdist = 0;                 // kullanici: Price yurudugu icin cok gec geliyordu -> kossunlar
		a = 360.0 * i / level.ekip.size;
		level.ekip[i].goalradius = 48;
		level.ekip[i] setgoalpos(zemin_bul(t + (cos(a) * (150 + (i % 3) * 70), sin(a) * (150 + (i % 3) * 70), 0)));
	}
	wait 20;
	flag_set("takviye_geldi");
}

arac_yola(v, gecikme)
{
	wait gecikme;
	if (isdefined(v))
		maps\_vehicle::gopath(v);
}

// durak dugumunde durur; oyuncu kasabaya girince surun boyunca uzaklasir ve gorulmeden silinir
crusader_durak(durak_ad)
{
	self endon("death");
	d = getvehiclenode(durak_ad, "targetname");
	self setwaitnode(d);
	self waittill("reached_wait_node");
	self setspeed(0, 12);
	self.durdu = true;
	while (!oyuncu_kasabada())
		wait 0.5;
	wait randomfloatrange(1, 4);
	self notify("ates_dur");
	self resumespeed(6);
	for (t = 0; ; t++)
	{
		wait 0.1;
		if (t > 120 && !gorunur(self.origin + (0, 0, 60)) && distance(self.origin, level.player.origin) > 1800)
			break;
	}
	self notify("olumsuz_bitti");
	self delete();
}

// kullanici: kasabaya girince bir daha disari cikilamaz (gercek gorunmez duvar)
kasabaya_kapat()
{
	while (!oyuncu_kasabada())
		wait 0.2;
	level.sinir = [];
	level.sinir[0] = (2960, 1260, 0);
	level.sinir[1] = (6040, 1260, 0);
	level.sinir[2] = (6040, 3740, 0);
	level.sinir[3] = (2960, 3740, 0);
	b = getent("kapi_engel_bati", "targetname");
	b movez(0 - 4000, 0.05);
	d = getent("kapi_engel_dogu", "targetname");
	d movez(0 - 4000, 0.05);
	level.dogu_engel = d;
}

oyuncu_kasabada()
{
	p = level.player.origin;
	return (p[0] > 2950 && p[0] < 6050 && p[1] > 1250 && p[1] < 3750);
}

gorunur(p)
{
	goz = level.player.origin + (0, 0, 60);
	ileri = anglestoforward(level.player getplayerangles());
	fark = vectornormalize(p - goz);
	if (vectordot(ileri, fark) < 0.35)
		return false;
	return sighttracepassed(goz, p, false, undefined);
}

durunca_isaretle()
{
	self endon("death");
	self waittill("reached_end_node");
	self.durdu = true;
}

// --------------------------------------------------------------------------
// 5) BASKIN: Crusaderlar sur MG'lerini ve buyuk kapiyi vurur
// --------------------------------------------------------------------------
crusader_baskini()
{
	for (t = 0; t < 80; t++)
	{
		n = 0;
		for (k = 0; k < level.crusader.size; k++)
			if (isdefined(level.crusader[k].durdu))
				n++;
		if (n >= 3)
			break;
		wait 0.5;
	}
	level thread asker_der("panzer");
	// sur MG yuvalari
	mg = getentarray("sur_mg", "targetname");
	for (i = 0; i < mg.size; i++)
	{
		c = level.crusader[i % level.crusader.size];
		c tank_vur(mg[i]);
		patlama(mg[i].origin);
		o = mg[i].origin;
		ai = getaiarray("axis");
		for (k = 0; k < ai.size; k++)
			if (distance(ai[k].origin, o) < 220)
				ai[k] dodamage(ai[k].health + 500, o);
		mg[i] thread mg_kaldir();
		// (duman kaldirildi: kullanici cok fazla dedi)
		wait 2;
	}
	// buyuk kapi: iki isabet; kanatlar devrilir, enkaz
	c = level.crusader[2];
	h = spawn("script_origin", level.kapi_m);
	c tank_vur(h);
	patlama(level.kapi_m);
	wait 2;
	c tank_vur(h);
	patlama(level.kapi_m);
	level.kapi notsolid();
	level.kapi rotateroll(80, 0.9, 0.7, 0);
	level.kapi movez(0 - 120, 0.9, 0.7, 0);
	parca_sac(level.kapi_m, 6);
	wait 0.9;
	level.kapi delete();
	level.kapi_enkaz moveto(level.kapi_enkaz.origin + (6656, 0, 0 - 2048), 0.05);
	wait 0.1;
	level.kapi_enkaz show();
	level.kapi_enkaz solid();
	// (duman kaldirildi: kullanici cok fazla dedi)
	h delete();
	flag_set("kapi_kirildi");
	// destek atisi: Crusaderlar ara sira surun ustune / kulelere
	level thread crusader_destek();
}

crusader_destek()
{
	hedef = [];
	hedef[0] = (2900, 1400, 360);
	hedef[1] = (2900, 3600, 360);
	hedef[2] = (3100, 1800, 200);
	hedef[3] = (3100, 3300, 200);
	while (level.asama == "BASKIN" || level.asama == "FLAK")
	{
		c = level.crusader[randomint(level.crusader.size)];
		if (isdefined(c) && !oyuncu_kasabada())
		{
			h = spawn("script_origin", hedef[randomint(hedef.size)]);
			c tank_vur(h);
			h delete();
		}
		wait randomfloatrange(5, 9);
	}
}

// sur MG'leri: nisanci yerinde kalir ve MG'yi birakmaz (burya dersi)
sur_mgleri()
{
	mg = getentarray("sur_mg", "targetname");
	sp = getentarray("sur_mg_alman", "targetname");
	for (i = 0; i < sp.size; i++)
	{
		g = dogur(sp[i]);
		sp[i] delete();
		if (!isdefined(g))
			continue;
		en = mg[0];
		for (k = 1; k < mg.size; k++)
			if (distance(mg[k].origin, g.origin) < distance(en.origin, g.origin))
				en = mg[k];
		g thread mg_birakma(en);
	}
}

mg_birakma(mg)
{
	self endon("death");
	self.goalradius = 4;
	self setgoalpos(self.origin);
	mg setmode("auto_ai");
	for (;;)
	{
		if (!isdefined(mg))
			return;
		sahip = mg getturretowner();
		if (!isdefined(sahip) || sahip != self)
			self useturret(mg);
		wait 1;
	}
}

// --------------------------------------------------------------------------
// 6) FLAKLAR: ates eder pozisyonda; murettebat olunce F ile patlayici, 5 sn
// --------------------------------------------------------------------------
flaklar_ates()
{
	f = getentarray("flak", "targetname");
	for (i = 0; i < f.size; i++)
		f[i] thread flak_ates();
}

flak_ates()
{
	self endon("imha");
	wait randomfloatrange(2, 8);
	for (;;)
	{
		if (isdefined(self.murettebat) && canli_say(self.murettebat) == 0)
			return;                                  // kullanici: murettebat olunce ates kesilir
		ileri = anglestoforward(self.angles);
		namlu = self.origin + vectorScale(ileri, 210) + (0, 0, 190);
		playfx(level._effect["flak_alev"], namlu, vectornormalize(ileri + (0, 0, 1.2)));
		playfx(level._effect["flak_toz"], self.origin + (0, 0, 10));
		self playsound("Flak88_fire");
		hava = self.origin + vectorScale(ileri, randomfloatrange(2500, 4500)) + (randomfloatrange(-800, 800), randomfloatrange(-800, 800), randomfloatrange(2200, 2900));
		playfx(level._effect["flak_puf"], hava);
		wait randomfloatrange(3.5, 6);
	}
}

flak_gorevi(i)
{
	no = self.script_noteworthy;
	t = undefined;
	tt = getentarray("flak_tetik", "targetname");
	for (k = 0; k < tt.size; k++)
		if (tt[k].script_noteworthy == no)
			t = tt[k];
	t tetik_ac();
	t sethintstring(&"KASRELBAB_PLATFORM_PATLAYICI");
	b = spawn("script_model", zemin_bul(self.origin + vectorScale(anglestoright(self.angles), 70)) - (0, 0, 4));   // kullanici: bomba havada duruyordu
	b.angles = self.angles;
	b thread obj_yanip_son("xmodel/military_tntbomb", "xmodel/military_tntbomb_obj");
	t waittill("trigger");
	t delete();
	b notify("yanip_son_dur");
	b setmodel("xmodel/military_tntbomb");
	b playsound("explo_plant_no_tick");
	b playloopsound("bomb_tick");
	wait 5;
	b stoploopsound();
	b delete();
	self notify("imha");
	o = self.origin + (0, 0, 60);
	playfx(level._effect["flak_patlama"], o);
	playfx(level._effect["tank_patlama"], o);
	earthquake(0.5, 1.5, o, 2000);
	s = spawn("script_origin", o);
	s playsound("explo_mine");
	radiusDamage(o, 300, 400, 100);
	self setmodel("xmodel/german_artillery_flak88_aa_d_static");
	parca_sac(o, 5);
	maps\_fx::loopfx("tank_ates", o, 0.6);
	maps\_fx::loopfx("tank_duman", o + (0, 0, 60), 3.5);
	objective_additionalposition(6, i, (0, 0, 0));    // kullanici: patlayan flakin yildizi sonsun
	level.flak_biten++;
}

obj_yanip_son(normal, obj)
{
	self endon("yanip_son_dur");
	self endon("death");
	for (;;)
	{
		self setmodel(obj);
		wait 0.5;
		self setmodel(normal);
		wait 0.35;
	}
}

// --------------------------------------------------------------------------
// 7) PANZER: cikis yolunu tutar; arkasina TNT (F), 5 sn
// --------------------------------------------------------------------------
panzer_son()
{
	a = maps\_vehicle::scripted_spawn(10);
	p = a[0];
	p thread arac_olumsuz();
	if (isdefined(level.dogu_engel))
		level.dogu_engel movez(4000, 0.05);       // clip_player araci da durdurur: Panzer gecerken kalkar
	level thread maps\_vehicle::gopath(p);
	level thread panzer_bagir(p);                     // kullanici: Panzer kapiya gelince bagirsinlar
	p waittill("reached_end_node");
	if (isdefined(level.dogu_engel))
		level.dogu_engel movez(0 - 4000, 0.05);
	ekip_hucum(level.meydan + (500, 0, 0), 700);
	price_der("tank");
	arka = getent("panzer_arka", "targetname").origin;
	objective_add(7, "active", &"KASRELBAB_OBJ_PANZER", arka);
	objective_current(7);
	// kullanici: sovyet bolumundeki gibi yapiskan bomba, tankin uzerinde (havada degil)
	b = spawn("script_model", p gettagorigin("tag_engine_left"));
	b.angles = p.angles + (0, 70, 0 - 90);
	b linkto(p, "tag_engine_left");
	b thread obj_yanip_son("xmodel/weapon_stickybomb", "xmodel/weapon_stickybomb_obj");
	t = getent("panzer_tetik", "targetname");
	t tetik_ac();
	t sethintstring(&"KASRELBAB_PLATFORM_PATLAYICI");
	level thread panzer_yardim(t, arka);             // kullanici: 140 sn icinde patlatilmazsa
	t waittill("trigger");
	level notify("panzer_kuruldu");
	t delete();
	b notify("yanip_son_dur");
	b setmodel("xmodel/weapon_stickybomb");
	b playsound("stickybomb_plant");
	b playloopsound("bomb_tick");
	sayac = maps\_utility::getstopwatch(60, 5);
	wait 5;
	sayac destroy();
	b stoploopsound();
	b delete();
	p notify("ates_dur");
	p notify("olumsuz_bitti");
	p.health = 1;
	p dodamage(50000, p.origin);
	p notify("death");
	earthquake(0.6, 1.5, p.origin, 2500);
	objective_state(7, "done");
	level thread asker_der("tamam");
	if (isdefined(level.dogu_engel))
		level.dogu_engel movez(4000, 0.05);
}

// 140 sn sonra rastgele 2 Ingiliz olumsuz olur, Panzer'e kosar, arkasina TNT kurar
panzer_yardim(t, arka)
{
	level endon("panzer_kuruldu");
	wait 140;
	aday = [];
	for (i = 0; i < level.ekip.size; i++)
		if (isalive(level.ekip[i]) && level.ekip[i] != level.price)
			aday[aday.size] = level.ekip[i];
	aday = karistir(aday);
	n = 0;
	for (i = 0; i < aday.size && n < 2; i++)
	{
		g = aday[i];
		g thread magic_bullet_shield();
		g notify("yeni_emir");
		g.ignoreall = true;
		g.goalradius = 24;
		g setgoalpos(zemin_bul(arka + (0 - 60 + n * 120, 0 - 80, 0)));
		n++;
	}
	for (k = 0; k < 60; k++)
	{
		yakin = 0;
		for (i = 0; i < n; i++)
			if (distance(aday[i].origin, arka) < 220)
				yakin++;
		if (yakin >= n)
			break;
		if (k > 30)
			for (i = 0; i < n; i++)
				if (!gorunur(aday[i].origin + (0, 0, 40)))
					aday[i] teleport(zemin_bul(arka + (0 - 60 + i * 120, 0 - 80, 0)));
		wait 0.5;
	}
	t notify("trigger");                             // asker TNT'yi kurar
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

panzer_ates()
{
	self endon("death");
	self endon("ates_dur");
	for (;;)
	{
		h = spawn("script_origin", level.player.origin + (randomfloatrange(-350, 350), randomfloatrange(-350, 350), 40));
		self tank_vur(h);
		h delete();
		wait randomfloatrange(5, 8);
	}
}

// --------------------------------------------------------------------------
// 8) CIKIS: kamyon; Price + 3 asker; F ile kasaya bin; Price konusur; kararma
// --------------------------------------------------------------------------
kamyon_cikis()
{
	a = maps\_vehicle::scripted_spawn(11);
	k = a[0];
	k thread arac_olumsuz();
	price_der("toplan");
	ileri = anglestoforward(k.angles);
	sag = anglestoright(k.angles);
	arka = k.origin - vectorScale(ileri, 260);            // kasa (dogu, kasabaya bakar)
	binen = [];
	if (isdefined(level.kamyon_ikili))
		for (i = 0; i < level.kamyon_ikili.size; i++)
			if (isalive(level.kamyon_ikili[i]))
				binen[binen.size] = level.kamyon_ikili[i];
	for (i = 0; i < level.ekip.size && binen.size < 2; i++)
		if (isalive(level.ekip[i]) && level.ekip[i] != level.price && !esit_var(binen, level.ekip[i]))
			binen[binen.size] = level.ekip[i];
	level.ekip_mod = "sahne";
	for (i = 0; i < level.ekip.size; i++)
		if (isalive(level.ekip[i]))
			level.ekip[i] notify("yeni_emir");
	// Price kasanin onune; iki asker kasaya tirmanma baslangic noktalarina (stok germantruck climbin)
	level.price.goalradius = 32;
	level.price setgoalnode(yakin_dugum(arka - vectorScale(ileri, 110) + vectorScale(sag, 110)));
	for (i = 0; i < binen.size; i++)
		binen[i] thread kasaya_hazirlan(k, i);
	objective_add(8, "active", &"KASRELBAB_OBJ_KAMYON", k.origin);
	objective_current(8);
	t = getent("kamyon_bin", "targetname");
	t tetik_ac();
	t sethintstring(&"KASRELBAB_PLATFORM_KAMYON");
	t waittill("trigger");
	t delete();
	objective_state(8, "done");
	// kasaya tirmanma (animasyonlu, hareket yok)
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
	level.muzik_son = true;
	level thread muzik_bir("kasrelbab_muzik_zafer");
	// AYNI ANDA: Price konusur + stok McGregor sahnesiyle (kamyon kapisi animasyonu dahil) surucuye biner;
	// iki asker kasaya atlar. Bekleme yok.
	level.kasaya_binen = 0;
	for (i = 0; i < binen.size; i++)
		binen[i] thread kasaya_bin(k, i);
	level thread price_der("kamyon");
	level.price.goalradius = 16;
	k maps\_anim::anim_reach_solo(level.price, "truckscene", "tag_driver", undefined, k);
	level.price.allowdeath = 0;
	k thread maps\kasrelbab_anim::kamyon_kapi_sahnesi();      // beltot: kamyonun kapi animasyonu + sesler
	k maps\_anim::anim_single_solo(level.price, "truckscene", "tag_driver", undefined, k);
	level.price linkto(k, "tag_driver");
	k thread maps\_anim::anim_loop_solo(level.price, "drive_loop", "tag_driver", "stop_idle");
	for (w = 0; w < 40 && level.kasaya_binen < binen.size; w++)
		wait 0.25;
	level thread price_der("final");
	// herkes hazir: kamyon bati kapisindan konvoy yoluna dogru; 3 sn sonra kararma
	b = getent("kapi_engel_bati", "targetname");
	b movez(4000, 0.05);
	wait 0.1;
	level thread maps\_vehicle::gopath(k);
	k setspeed(9, 4);
	wait 6;                                      // kullanici: kamyon kalktiktan 6 sn sonra kararma
	bolum_sonu();
}

// --------------------------------------------------------------------------
// ORTAK (kumtepe)
// --------------------------------------------------------------------------
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

arac_olumsuz()
{
	self endon("death");
	self endon("olumsuz_bitti");
	for (;;)
	{
		self.health = 100000;
		self waittill("damage");
	}
}

tank_vur(hedef)
{
	self endon("death");
	self setturrettargetent(hedef, (0, 0, 0));
	self waittill_turret(3);
	self notify("turret_fire");
	wait 0.3;
	self clearturrettarget();
}

waittill_turret(sure)
{
	self endon("turret_on_target");
	wait sure;
}

patlama(o)
{
	s = spawn("script_origin", o);
	s playsound("mortar_incoming1");
	wait 0.35;
	playfx(level._effect["tank_patlama"], o);
	playfx(level._effect["duvar_patlama"], o + (40, 0, 0));
	earthquake(0.5, 1.5, o, 1800);
	s playsound("explo_mine");
	s thread sil_sonra(5);
}

sil_sonra(sure)
{
	wait sure;
	if (isdefined(self))
		self delete();
}

parca_sac(o, adet)
{
	m = [];
	m[0] = "xmodel/egypt_prop_buildingpiece01";
	m[1] = "xmodel/egypt_prop_buildingpiece02";
	m[2] = "xmodel/egypt_prop_buildingpiece03";
	for (i = 0; i < adet; i++)
	{
		p = spawn("script_model", o + (randomfloatrange(-80, 80), randomfloatrange(-80, 80), randomfloatrange(0, 60)));
		p setmodel(m[randomint(m.size)]);
		p.angles = (randomint(360), randomint(360), randomint(360));
		p thread parca_dus();
	}
}

parca_dus()
{
	self movegravity((randomfloatrange(-200, 200), randomfloatrange(-200, 200), randomfloatrange(150, 380)), 1.4);
	self rotatevelocity((randomfloatrange(-300, 300), randomfloatrange(-300, 300), randomfloatrange(-300, 300)), 1.4);
	wait 2.2;
	self delete();
}

dogur(sp)
{
	for (t = 0; t < 80; t++)
	{
		if (getaiarray().size < 32)
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

grup_dogur(ad)
{
	sp = getentarray(ad, "targetname");
	dogan = [];
	for (i = 0; i < sp.size; i++)
	{
		g = dogur(sp[i]);
		nobet = isdefined(sp[i].script_noteworthy) && sp[i].script_noteworthy == "nobet";
		sp[i] delete();
		if (!isdefined(g))
			continue;
		dogan[dogan.size] = g;
		if (nobet)
			g thread nobet_dolas();
		else
			g thread bolge_dolas(g.origin, 350, -9999, 9999);
		wait 0.1;
	}
	return dogan;
}

nobet_dolas()
{
	self endon("death");
	merkez = self.origin;
	self.goalradius = 32;
	while (!isdefined(self.enemy))
	{
		a = randomfloat(360);
		self setgoalpos(zemin_bul(merkez + (cos(a) * 220, sin(a) * 220, 0)));
		wait randomfloatrange(5, 9);
	}
}

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

hedef_bekle(sure)
{
	self endon("goal");
	wait sure;
}

bolge_dolas(merkez, yaricap, zmin, zmax)
{
	self endon("death");
	self endon("yeni_emir");
	wait randomfloatrange(1, 4);
	for (;;)
	{
		p = level.player.origin;
		aday = [];
		for (i = 0; i < level.siper.size; i++)
		{
			n = level.siper[i];
			if (distance((n.origin[0], n.origin[1], 0), (merkez[0], merkez[1], 0)) > yaricap)
				continue;
			dn = distance(n.origin, self.origin);
			if (dn < 100 || dn > 750)
				continue;
			if (self.team == "axis" && distance(n.origin, p) < 300)
				continue;
			aday[aday.size] = n;
		}
		if (aday.size)
		{
			self.goalradius = 80;
			self setgoalnode(aday[randomint(aday.size)]);
			self hedef_bekle(10);
		}
		wait randomfloatrange(6, 12);
	}
}

ekip_beyni()
{
	for (;;)
	{
		wait 1;
		ai = [];
		for (i = 0; i < level.ekip.size; i++)
			if (isalive(level.ekip[i]))
				ai[ai.size] = level.ekip[i];
		if (level.ekip_mod == "hucum")
			ekip_hucum_et(ai);
	}
}

ekip_hucum(merkez, yaricap)
{
	level.hucum_siper = [];
	for (i = 0; i < level.siper.size; i++)
		if (distance((level.siper[i].origin[0], level.siper[i].origin[1], 0), (merkez[0], merkez[1], 0)) < yaricap)
			level.hucum_siper[level.hucum_siper.size] = level.siper[i];
	if (level.hucum_siper.size)
		level.ekip_mod = "hucum";
}

ekip_hucum_et(ai)
{
	for (i = 0; i < ai.size; i++)
	{
		g = ai[i];
		g.pathenemyfightdist = 500;
		g.pathenemylookahead = 500;
		n = level.hucum_siper[i % level.hucum_siper.size];
		if (isdefined(g.hucum_zaman) && gettime() < g.hucum_zaman)
			continue;
		g.hucum_zaman = gettime() + randomintrange(5000, 8000);
		hedef = n.origin;
		if (distance(g.origin, n.origin) > 400)
		{
			ara = g.origin + vectorScale(vectornormalize(n.origin - g.origin), 350);
			s = siper_bul(ara, 300);
			if (isdefined(s))
				hedef = s.origin;
			else
				hedef = zemin_bul(ara);
		}
		g.goalradius = 72;
		g setgoalpos(hedef);
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

zemin_bul(nokta)
{
	tr = bulletTrace(nokta + (0, 0, 400), nokta - (0, 0, 800), false, undefined);
	return tr["position"] + (0, 0, 4);
}

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
	perde fadeOverTime(6);
	perde.alpha = 1;
	wait 6.5;
	test_yaz("GOREV TAMAM");
	missionSuccess("credits", false);
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
	for (t = 0; t < 120; t++)
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
		ses_cal(g, "kasrelbab_price_" + replik, 12);
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
	org waittill_any_timeout_kb(sure, "ses_bitti", "yok");
	org delete();
}

waittill_any_timeout_kb(sure, a, b)
{
	self endon(a);
	self endon(b);
	wait sure;
}

asker_der(ad)
{
	konusan = level.player;
	for (i = 0; i < level.ekip.size; i++)
		if (isalive(level.ekip[i]) && (!isdefined(level.price) || level.ekip[i] != level.price))
		{
			konusan = level.ekip[i];
			break;
		}
	ses_cal(konusan, "kasrelbab_asker_" + ad, 8);
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

sinir_bekcisi()
{
	son = level.player.origin;
	disari = 0;
	for (;;)
	{
		p = level.player.origin;
		if (cokgen_icinde(p, level.sinir))
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
// EKRAN TURU (kr_tur 1)
// --------------------------------------------------------------------------
ekran_turu()
{
	level.player takeallweapons();
	level thread test_olumsuz();
	n = [];
	a = [];
	n[n.size] = (0, 0, 9000);         a[a.size] = (89, 90, 0);    // 1 tum harita
	n[n.size] = (4500, 2500, 3200);   a[a.size] = (89, 90, 0);    // 2 kasaba ustten
	n[n.size] = (-6350, -4780, 380);  a[a.size] = (2, 80, 0);     // 3 cali -> konvoy yolu
	n[n.size] = (-6350, -4780, 380);  a[a.size] = (2, 30, 0);     // 4 cali -> kasaba yonu
	n[n.size] = (-6350, -4780, 380);  a[a.size] = (2, 200, 0);    // 5 cali arkasi (takviye vadisi)
	n[n.size] = (-6600, -5200, 600);  a[a.size] = (25, 40, 0);    // 6 cali ve agac ustten
	n[n.size] = (-8400, -3300, 300);  a[a.size] = (4, 60, 0);     // 7 viewpos1 konvoy gelisi
	n[n.size] = (-1300, -3800, 300);  a[a.size] = (4, 320, 0);    // 8 viewpos2 konvoy sonu
	n[n.size] = (-1800, -1700, 160);  a[a.size] = (6, 90, 0);     // 9 kulube on
	n[n.size] = (-1800, -1230, 100);  a[a.size] = (4, 90, 0);     // 10 kulube ic, telsiz
	n[n.size] = (-2300, -1700, 300);  a[a.size] = (6, 40, 0);     // 11 toplanma -> kasaba
	n[n.size] = (1500, 2500, 260);    a[a.size] = (4, 0, 0);      // 12 sur ve buyuk kapi
	n[n.size] = (2600, 2500, 180);    a[a.size] = (6, 0, 0);      // 13 buyuk kapi yakin
	n[n.size] = (2500, 1200, 300);    a[a.size] = (6, 40, 0);     // 14 sur kosesi kule
	n[n.size] = (3200, 2500, 120);    a[a.size] = (4, 0, 0);      // 15 ana sokak
	n[n.size] = (4000, 2450, 140);    a[a.size] = (6, 0, 0);      // 16 meydan + flak 1
	n[n.size] = (4500, 3100, 140);    a[a.size] = (6, 90, 0);     // 17 kuzey avlu + flak 2
	n[n.size] = (5400, 2860, 140);    a[a.size] = (6, 0, 0);      // 18 dogu + flak 3
	n[n.size] = (3450, 1750, 100);    a[a.size] = (4, 0, 0);      // 19 konak ic
	n[n.size] = (3450, 3300, 100);    a[a.size] = (4, 0, 0);      // 20 han ic
	n[n.size] = (5550, 1700, 100);    a[a.size] = (4, 0, 0);      // 21 depo ic
	n[n.size] = (5450, 3350, 100);    a[a.size] = (4, 0, 0);      // 22 cami ic
	n[n.size] = (5000, 3300, 400);    a[a.size] = (8, 30, 0);     // 23 minare
	n[n.size] = (6573, 978, 300);     a[a.size] = (6, 95, 0);     // 24 Panzer yolu (3)->(4)
	n[n.size] = (5700, 2600, 160);    a[a.size] = (6, 0, 0);      // 25 Panzer duragi (5)
	n[n.size] = (4300, -4600, 500);   a[a.size] = (6, 60, 0);     // 26 guney kervan yolu
	n[n.size] = (3500, 2500, 160);    a[a.size] = (6, 180, 0);    // 27 final kamyonu (6)
	n[n.size] = (-7800, 0, 400);      a[a.size] = (4, 180, 0);    // 28 bati ufuk
	n[n.size] = (-6350, -4780, 380);  a[a.size] = (2, 330, 0);    // 29 cali -> GD (S/E)
	n[n.size] = (6600, -1700, 500);   a[a.size] = (6, 300, 0);    // 30 dogu yol birlesimi
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

// --------------------------------------------------------------------------
// GOREV AKISI TESTI (kr_tur 2): otomatik oyuncu, her asamayi konsola yazar
tl(m)
{
	println("KRTEST " + int(gettime() / 1000) + "s " + m);
	test_yaz(m);
}

akis_testi()
{
	level thread test_olumsuz();
	level thread akis_izle();
	wait 1;
	level.player allowstand(false);
	level.player allowcrouch(false);
	while (level.asama != "KULUBE")
	{
		if (flag("tespit")) { tl("HATA tespit edildi (yatarken)"); flag_clear("tespit"); }
		wait 0.5;
	}
	level.player allowstand(true);
	level.player allowcrouch(true);
	wait 2;
	level.player setorigin(zemin_bul(level.kulube + (0, 0 - 380, 0)));
	ai = getaiarray("axis");
	tl("kulube axis canli: " + ai.size);
	wait 3;
	ai = getaiarray("axis");
	for (i = 0; i < ai.size; i++)
		if (distance(ai[i].origin, level.kulube) < 600)
			ai[i] dodamage(ai[i].health + 500, ai[i].origin);
	while (level.asama != "TELSIZ") wait 0.3;
	wait 2;
	getent("telsiz_tetik", "targetname") notify("trigger", level.player);
	while (!isdefined(level.price)) wait 0.5;
	tl("price + ekip dogdu: " + level.ekip.size);
	while (level.asama == "TAKVIYE")
	{
		if (isalive(level.price) && distance(level.price.origin, level.kulube) < 900)
			level.player setorigin(zemin_bul(level.price.origin + (0, 0 - 120, 0)));
		else
			level.player setorigin(zemin_bul(level.kulube + (0, 0 - 380, 0)));
		wait 2;
	}
	tl("brifing gecildi, price kulubeye vardi");
	wait 8;
	level.player setorigin(zemin_bul(level.kapi_m + (0 - 700, 0, 0)));
	flag_wait("kapi_kirildi");
	tl("kapi devrildi, crusader ates etti");
	wait 6;
	level.player setorigin(zemin_bul(level.kapi_m + (300, 0, 0)));
	while (level.asama == "BASKIN")
	{
		ai = getaiarray("axis");
		if (ai.size)
		{
			k = ai[randomint(ai.size)];
			if (!isdefined(k.flakci))
				k dodamage(k.health + 500, k.origin);
		}
		wait 1.5;
	}
	while (level.asama == "FLAK")
	{
		f = getentarray("flak", "targetname");
		for (i = 0; i < f.size; i++)
			if (isdefined(f[i].murettebat))
				for (k = 0; k < f[i].murettebat.size; k++)
					if (isalive(f[i].murettebat[k]))
						f[i].murettebat[k] dodamage(5000, f[i].origin);
		t = getentarray("flak_tetik", "targetname");
		if (t.size)
		{
			level.player setorigin(zemin_bul(t[0].origin + (0, 0 - 150, 0)));
			wait 1;
			t[0] notify("trigger", level.player);
		}
		wait 7;
		tl("flak biten: " + level.flak_biten);
	}
	while (level.asama == "PANZER")
	{
		t = getent("panzer_tetik", "targetname");
		if (isdefined(t) && t.origin[2] > -5000)
		{
			wait 10;
			if (isdefined(t))
				t notify("trigger", level.player);
			break;
		}
		wait 1;
	}
	while (level.asama != "CIKIS") wait 0.5;
	wait 4;
	level.player setorigin(zemin_bul(getent("kamyon_yan", "targetname").origin));
	wait 2;
	getent("kamyon_bin", "targetname") notify("trigger", level.player);
	tl("kamyona binildi");
}

akis_izle()
{
	son = "";
	for (;;)
	{
		if (level.asama != son)
		{
			son = level.asama;
			tl("ASAMA " + son);
		}
		ek = 0;
		if (isdefined(level.ekip))
			ek = canli_say(level.ekip);
		k = "-";
		if (isdefined(level.kasaba_kalan))
			k = "" + level.kasaba_kalan;
		pr = "-";
		if (isdefined(level.price) && isalive(level.price))
			pr = "" + int(level.price.origin[0]) + "," + int(level.price.origin[1]);
		setcvar("kr_durum", son + " price=" + pr + " ekip0=" + ekip_yer() + " pz=" + panzer_yer() + " ai=" + getaiarray().size + " axis=" + getaiarray("axis").size + " ekip=" + ek + " kalan=" + k);
		println("KRTEST durum " + son + " ai=" + getaiarray().size + " axis=" + getaiarray("axis").size + " ekip=" + ek + " kasaba_kalan=" + k + " price=" + pr + " oyuncu=" + int(level.player.origin[0]) + "," + int(level.player.origin[1]));
		wait 15;
	}
}

// nisanci animasyonu bitmeden turret silinirse mg42/stand.gsc runtime hatasi verir
mg_kaldir()
{
	wait 1.5;
	self hide();
}

panzer_yer()
{
	v = getentarray("script_vehicle", "classname");
	for (i = 0; i < v.size; i++)
		if (isdefined(v[i].vehicletype) && v[i].vehicletype == "panzer2" && isdefined(v[i].script_vehiclespawngroup) && v[i].script_vehiclespawngroup == 10)
			return "" + int(v[i].origin[0]) + "," + int(v[i].origin[1]);
	return "-";
}

// kullanici: Price dogdugu yerde kaldi -> 8 sn kimildamazsa, oyuncu gormuyorken en yakin ekip arkadasinin yanina
takilma_bekcisi()
{
	self endon("death");
	son = self.origin;
	sure = 0;
	for (;;)
	{
		wait 1;
		if (level.asama != "TAKVIYE")
			return;                                   // yalniz kulubeye gelis icin
		if (!isdefined(self.hedef_yer) || distance(self.origin, self.hedef_yer) < 200)
		{
			son = self.origin; sure = 0;
			continue;
		}
		if (distance(self.origin, son) > 60)
		{
			son = self.origin; sure = 0;
			continue;
		}
		sure++;
		if (sure < 8 || gorunur(self.origin + (0, 0, 40)))
			continue;
		en = undefined;
		for (i = 0; i < level.ekip.size; i++)
			if (isalive(level.ekip[i]) && level.ekip[i] != self && distance(level.ekip[i].origin, son) > 300)
				if (!isdefined(en) || distance(level.ekip[i].origin, self.hedef_yer) < distance(en.origin, self.hedef_yer))
					en = level.ekip[i];
		if (isdefined(en) && !gorunur(en.origin + (0, 0, 40)))
		{
			self teleport(zemin_bul(en.origin + (0 - 60, 40, 0)));
			self setgoalnode(yakin_dugum(self.hedef_yer));
		}
		son = self.origin; sure = 0;
	}
}

ekip_yer()
{
	if (!isdefined(level.ekip))
		return "-";
	m = "";
	for (i = 0; i < level.ekip.size && i < 4; i++)
		if (isalive(level.ekip[i]))
			m = m + int(level.ekip[i].origin[0]) + "," + int(level.ekip[i].origin[1]) + " ";
	return m;
}

// en yakin pathnode (kullanilmamis); AI rotasi her zaman gercek dugume
yakin_dugum(p)
{
	if (!isdefined(level.tum_dugum))
		level.tum_dugum = getallnodes();
	en = undefined;
	ed = 999999;
	for (i = 0; i < level.tum_dugum.size; i++)
	{
		d_ = level.tum_dugum[i];
		if (d_.type != "Path" || isdefined(d_.kapildi))
			continue;
		u = distance(d_.origin, p);
		if (u < ed)
		{
			ed = u;
			en = d_;
		}
	}
	en.kapildi = true;
	return en;
}

// ekipten 900+ geride, 10 sn kimildamayan asker oyuncu gormuyorken Price'in yanina alinir
geride_kalma()
{
	self endon("death");
	son = self.origin;
	sure = 0;
	for (;;)
	{
		wait 1;
		if (distance(self.origin, son) > 60 || !isdefined(level.price) || !isalive(level.price) || distance(self.origin, level.price.origin) < 900)
		{
			son = self.origin; sure = 0;
			continue;
		}
		sure++;
		if (sure < 10 || gorunur(self.origin + (0, 0, 40)) || gorunur(level.price.origin + (0, 0, 40)))
			continue;
		self teleport(zemin_bul(level.price.origin + (randomintrange(-90, 90), randomintrange(-90, 90), 0)));
		son = self.origin; sure = 0;
	}
}

// Price gec kalirsa (ekip toplandi, o uzakta, gorunmuyor) toplanmaya yetisir
price_yetistir()
{
	if (!isdefined(level.price) || !isalive(level.price))
		return;
	t = getent("toplanma", "targetname").origin;
	if (distance(level.price.origin, t) < 900 || gorunur(level.price.origin + (0, 0, 40)))
		return;
	n = 0;
	for (i = 0; i < level.ekip.size; i++)
		if (isalive(level.ekip[i]) && distance(level.ekip[i].origin, t) < 700)
			n++;
	if (n < 4)
		return;
	d = yakin_dugum(t + (0 - 180, 0 - 120, 0));
	if (gorunur(d.origin + (0, 0, 40)))
		return;
	level.price teleport(d.origin);
	level.price setgoalnode(d);
}

// ekibi bir noktanin cevresindeki GERCEK dugumlere dagit (setgoalnode: rota hep bulunur)
ekip_noktaya(merkez, ic, dis)
{
	for (i = 0; i < level.ekip.size; i++)
	{
		g = level.ekip[i];
		if (!isalive(g))
			continue;
		g notify("yeni_emir");
		g.walkdist = 0;
		g.goalradius = 64;
		a = 360.0 * i / level.ekip.size + randomfloat(20);
		r = ic + randomfloat(dis);
		n = yakin_dugum(merkez + (cos(a) * r, sin(a) * r, 0));
		g.hedef_yer = n.origin;
		g setgoalnode(n);
	}
}

ekip_hucum_gecikmeli(merkez, yaricap, sure)
{
	wait sure;
	ekip_hucum(merkez, yaricap);
}

panzer_bagir(p)
{
	p endon("death");
	while (distance((p.origin[0], p.origin[1], 0), (6347, 2609, 0)) > 600)
		wait 0.2;
	asker_der("panzer");
}

// Panzer'den once cikis yolundan 10 Alman kasabaya saldirir
dogu_saldirisi()
{
	sp = getentarray("dogu_alman", "targetname");
	ai = [];
	for (i = 0; i < sp.size; i++)
	{
		g = dogur(sp[i]);
		sp[i] delete();
		if (!isdefined(g))
			continue;
		ai[ai.size] = g;
		g.goalradius = 300;
		g setgoalnode(yakin_dugum(level.meydan + (500 + randomint(400), randomintrange(-400, 400), 0)));
		g thread dogu_ajan();
		wait 0.3;
	}
	for (t = 0; t < 240; t++)
	{
		if (canli_say(ai) <= 2)
			break;
		wait 0.5;
	}
}

dogu_ajan()
{
	self endon("death");
	wait randomfloatrange(8, 14);
	self thread bolge_dolas(level.meydan + (400, 0, 0), 700, -9999, 9999);
}

esit_var(d, e)
{
	for (i = 0; i < d.size; i++)
		if (d[i] == e)
			return true;
	return false;
}

// tirmanma animasyonunun baslangic noktasina git ve bekle
kasaya_hazirlan(k, i)
{
	self endon("death");
	cn = k gettagorigin("tag_climbnode");
	ca = k gettagangles("tag_climbnode");
	an = level.kr_anim["kasa_tirman"][i];
	self.kasa_bas = getstartorigin(cn, ca, an);
	self.goalradius = 16;
	self allowedstances("stand");
	self setgoalpos(self.kasa_bas);
}

// stok germantruck buddyjump: tag_climbnode'a bagli climbin, sonra koltuk etiketinde ayakta bekleme
kasaya_bin(k, i)
{
	self endon("death");
	cn = k gettagorigin("tag_climbnode");
	ca = k gettagangles("tag_climbnode");
	an = level.kr_anim["kasa_tirman"][i];
	bas = getstartorigin(cn, ca, an);
	for (w = 0; w < 40 && distance(self.origin, bas) > 40; w++)
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

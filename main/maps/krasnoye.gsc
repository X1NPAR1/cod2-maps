// ==========================================================================
// krasnoye.gsc -- karli kolhoz koyu. Sovyet: koyu temizle, karsi saldiriyi
// (kamyon -> yari paletli -> Panzer II) puskurt, tanki yapiskan bombayla vur.
//
// Kaliplar stok Sovyet bolumlerinden (iwd'den okundu):
//   takviye ......... maps\_spawner friendly_wave (cityhall/tankhunt)
//   dost hareketi ... level.friendlyMethod "friendly chains" + setfriendlychain
//   bolge temizligi . waittill_aigroupcleared (trainyard_obj)
//   araclar ......... maps\_vehicle::scripted_spawn + gopath (tankhunt)
//   yapiskan bomba .. tank_explosives / tank_runup (tankhunt birebir)
//   replik .......... level.scrsound + anim_single_solo (tankhunt_anim)
// ==========================================================================
#include maps\_utility;
#include maps\_anim;
#using_animtree("generic_human");

main()
{
	setExpFog(0.00026, .64, .65, .68, 0);
	setCullDist(12000);

	precacheModel("xmodel/weapon_stickybomb");
	precacheModel("xmodel/weapon_stickybomb_obj");
	precacheShader("inventory_stickybomb");
	precacheShader("hudStopwatch");
	precacheShader("hudStopwatchNeedle");
	precacheString(&"SCRIPT_EXPLOSIVESPLANTED");
	precacheString(&"TANKHUNT_PLATFORM_PLANT_STICKY_BOMB");
	precacheString(&"TANKHUNT_PLATFORM_PICK_UP_STICKY_BOMBS");
	precacheString(&"KRASNOYE_OBJ_KOY");
	precacheString(&"KRASNOYE_OBJ_SAVUNMA");
	precacheString(&"KRASNOYE_OBJ_PUSKURT");
	precacheString(&"KRASNOYE_OBJ_BOMBA");
	precacheString(&"KRASNOYE_OBJ_TANK");
	precacheString(&"KRASNOYE_BITTI");
	precacheString(&"KRASNOYE_INTRO_TITLE");
	precacheString(&"KRASNOYE_INTRO_PLACE");
	precacheString(&"KRASNOYE_INTRO_DATE");
	precacheString(&"KRASNOYE_INTRO_INFO");
	precacheShader("black");
	precacheItem("smoke_grenade_american");     // demolition throwSmoke

	level.campaign = "russian";
	maps\_truck::main("xmodel/vehicle_opel_blitz_snow");
	maps\_halftrack::main("xmodel/vehicle_halftrack_mg_snow");
	maps\_panzer2::main("xmodel/vehicle_panzer_ii_winter");
	maps\_panzer2::main("xmodel/vehicle_panzer_II_winter_r_tread_d");
	maps\_panzer2::main("xmodel/vehicle_panzer_II_winter_l_tread_d");
	// stok duhoc_defend/elalamein: friendly_wave sayaci _load'dan once
	// baslatilir; yoksa _spawner.gsc:2817 "undefined < int" ile coker (olculdu)
	level.totalfriends = 0;
	level.maxfriendlies = 7;
	maps\krasnoye_fx::main();
	maps\_load::main();
	maps\krasnoye_anim::main();
	setEnvironment("cold");

	// tankhunt.gsc main() ile ayni dost ayarlari
	level.maxfriendlies = 7;                    // oyuncu + 7 = 8 kisi
	level.friendlyMethod = "friendly chains";
	level.friendlywave_thread = ::friendlyMethod;
	level.followmin = -2;
	level.followmax = 2;
	level.timersused = 0;
	level.player.stickybomb = 0;
	level.runups = 0;

	flag_init("koy_temiz");
	flag_init("yapiskan_alindi");
	flag_init("tank_bitti");

	// ACILIS SIRASINDA TAKVIYE YOK: friendly_wave tetikleri kapali (stok
	// triggerOff/triggerOn, demolition.gsc). Yoksa ekip sayilmadan once
	// takviye dogup zincirsiz oyuncuyu izlemeye kalkiyor -> olumcul hata:
	// "Sentient ... following the sentient player ... not on a friendly chain"
	getent("yapiskan_al", "targetname") triggerOff();   // tank gelene kadar alinamaz
	getent("yapiskan_model", "targetname") hide();      // tank koye girince belirir
	level.dalga_tetik = getentarray("friendly_wave", "targetname");
	for (i = 0; i < level.dalga_tetik.size; i++)
		level.dalga_tetik[i] triggerOff();
	// oyuncu HER ZAMAN bir zincirde olmali (ayni hata)
	// (tur modunda da gecerli -- once burada, sonra tur kontrolu)
	level.player setfriendlychain(getnode("fc1", "targetname"));

	if (getcvar("kr_tur") != "" && getcvar("kr_tur") != "0")
	{
		level thread ekran_turu();
		return;
	}

	oyuncu_techizat();
	level thread tanitim();
	ekip_kur();
	level thread zincir_ilerlet();
	level thread takviye_bildir();
	siper_onbellek();
	level thread dost_bekcisi();
	level thread gorevler();
}

// --------------------------------------------------------------------------
// TANITIM EKRANI -- stok maps\_introscreen.gsc introscreen_delay() birebir
// (siyah perde + baslik/yer/tarih/bilgi satirlari), tek fark: kullanici
// istegi ile perde 3 saniyede kalkar (stok 1.5).
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
	musicplay("krasnoye_muzik_giris");          // kullanici: muzik acilis ekraninda baslasin
	wait .05;
	level.introstring = [];
	maps\_introscreen::introscreen_create_line(&"KRASNOYE_INTRO_TITLE");
	wait 2;
	maps\_introscreen::introscreen_create_line(&"KRASNOYE_INTRO_PLACE");
	maps\_introscreen::introscreen_create_line(&"KRASNOYE_INTRO_DATE");
	wait 2;
	maps\_introscreen::introscreen_create_line(&"KRASNOYE_INTRO_INFO");
	wait 3;
	level.introblack fadeOverTime(3);
	level.introblack.alpha = 0;
	level.player freezeControls(false);
	maps\_introscreen::introscreen_fadeOutText();
	level notify("tanitim_bitti");
}

// --------------------------------------------------------------------------
// OYUNCU TECHIZATI (kullanici istegi): PPSh birincil, TT-30 tabanca,
// 4 el bombasi, 4 duman. _loadout.gsc ile ayni API (giveWeapon,
// setWeaponClipAmmo, switchToWeapon, setup_russian el gorunumu).
// --------------------------------------------------------------------------
oyuncu_techizat()
{
	level.player takeallweapons();
	level.player giveWeapon("ppsh");
	level.player giveWeapon("svt40");
	level.player giveWeapon("RGD-33russianfrag");
	level.player giveWeapon("smoke_grenade_russian");
	level.player giveMaxAmmo("ppsh");
	level.player giveMaxAmmo("svt40");
	level.player setWeaponClipAmmo("RGD-33russianfrag", 4);
	level.player setWeaponClipAmmo("smoke_grenade_russian", 4);
	level.player switchToWeapon("ppsh");
	level.player switchToOffhand("RGD-33russianfrag");
	maps\_loadout::setup_russian();
}

// --------------------------------------------------------------------------
// EKIP: Leonov (olumsuz) + 6 asker. friendly_wave sayaci bunlari
// _spawner friendlydeath_thread ile sayar; biri olunce gorus disindaki
// takviye spawner'larindan yenisi dogar (maxfriendlies = 7).
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
	daire_kur();
}

// --------------------------------------------------------------------------
// ACILIS: koyden uzakta (kuzey sirtinin arkasi) 8 kisilik cember. Askerler
// comelmis, yuzleri ortaya donuk; oyuncu da cemberde, ortaya bakar.
// (allowedstances / orientmode "face angle" -- stok _halftrack, _patrol)
// --------------------------------------------------------------------------
daire_kur()
{
	merkez = (0, 2780, 0);
	tr = bulletTrace(merkez + (0, 0, 600), merkez - (0, 0, 600), false, undefined);
	merkez = tr["position"];
	level.daire_merkez = merkez;
	n = level.ekip.size + 1;                    // +1 oyuncu
	r = 120;
	for (i = 0; i <= level.ekip.size; i++)
	{
		a = 360.0 * i / n + 270;                // oyuncu guneyde (koye arkasi donuk degil)
		p = merkez + (cos(a) * r, sin(a) * r, 0);
		tr = bulletTrace(p + (0, 0, 200), p - (0, 0, 400), false, undefined);
		p = tr["position"];
		yaw = vectortoangles(merkez - p)[1];
		if (i == 0)
		{
			level.player setorigin(p + (0, 0, 4));
			level.player setplayerangles((10, yaw, 0));
			continue;
		}
		g = level.ekip[i - 1];
		g.daire_yaw = yaw;
		g teleport(p + (0, 0, 4));
		g.goalradius = 8;
		g setgoalpos(p);
		g allowedstances("crouch");
		g orientmode("face angle", yaw);
		g thread daire_bak();
	}
}

// cemberde yuzunu ortaya tutar (AI kendi kendine donmesin)
daire_bak()
{
	self endon("death");
	level endon("daire_bitti");
	for (;;)
	{
		self orientmode("face angle", self.daire_yaw);
		wait 0.5;
	}
}

// konusma bitince herkes kalkar, oyuncuyu izler; ilk zincir siper hatti
daire_dagil()
{
	level notify("daire_bitti");
	for (i = 0; i < level.ekip.size; i++)
	{
		g = level.ekip[i];
		if (!isalive(g))
			continue;
		g allowedstances("stand", "crouch", "prone");
		g orientmode("face default");
		friendlyMethod(g);
	}
	// herkes AYNI zincirde: once cemberin hemen guneyi (fc0), zincir_ilerlet
	// oyuncu ilerledikce fc1 (siper) -> fc2 -> fc3'e gecirir
	level.player setfriendlychain(getnode("fc0", "targetname"));
	for (i = 0; i < level.dalga_tetik.size; i++)
		level.dalga_tetik[i] triggerOn();
}

friendlyMethod(guy)
{
	if (!isdefined(guy))
		guy = self;
	guy.followmin = level.followmin;
	guy.followmax = level.followmax;
	guy.friendlyWaypoint = false;
	guy.goalradius = 320;                      // oyuncu cevresindeki siperleri kullanir
	guy setgoalentity(level.player);
}

// oyuncu ilerledikce zincir degisir (stok trigger_friendlychain ile ayni is)
zincir_ilerlet()
{
	level endon("savunma_basladi");
	level waittill("daire_bitti");
	asama = 0;
	for (;;)
	{
		wait 0.5;
		y = level.player.origin[1];
		if (asama == 0 && y < 2400)
		{
			asama = 1;
			level.player setfriendlychain(getnode("fc1", "targetname"));
		}
		else if (asama == 1 && y < 1500)
		{
			asama = 2;
			level.player setfriendlychain(getnode("fc2", "targetname"));
		}
		else if (asama == 2 && y < 750)
		{
			asama = 3;
			level.player setfriendlychain(getnode("fc3", "targetname"));
			level thread leonov_der("evler");
		}
	}
}

// takviye dogdugunda (friendly_wave) Leonov arada bir haber verir
takviye_bildir()
{
	son = 0;
	for (;;)
	{
		level waittill("friendly_died");
		if (gettime() - son < 240000)          // 4 dakikada en fazla bir kez
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

// Leonov replik: stok Dialogue_Thread (tankhunt) kalibi
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

// --------------------------------------------------------------------------
// GOREV AKISI
// --------------------------------------------------------------------------
gorevler()
{
	// koy savunuculari: oyuncu gorse de dogsunlar (stalingradspawn = zorla)
	sp = getentarray("koy_alman", "targetname");
	for (i = 0; i < sp.size; i++)
	{
		guy = sp[i] stalingradspawn();
		if (!spawn_failed(guy) && !issubstr(guy.classname, "mg42portable"))
			guy thread koy_savunucu();
	}
	// waittill_aigroupcleared SPAWNER sayisini da bekler (_utility.gsc:1821);
	// kullanilmayan spawner sayaci sifirlamiyordu -> koy temiz olsa da gorev
	// bitmiyordu (kullanici testi). Stok kill_spawnerNum gibi spawner silinir.
	wait 0.5;
	for (i = 0; i < sp.size; i++)
		if (isdefined(sp[i]))
			sp[i] delete();

	level waittill("tanitim_bitti");
	wait 1.5;
	leonov_der("giris");
	wait 0.5;
	leonov_der("ilerle");
	wait 0.5;
	daire_dagil();
	level thread muzik("krasnoye_muzik_koy");
	objective_add(1, "active", &"KRASNOYE_OBJ_KOY", (-250, 300, 0));
	objective_current(1);

	waittill_aigroupcleared("koy");
	flag_set("koy_temiz");
	objective_state(1, "done");
	autoSaveByName("koy_temiz");
	level thread muzik_sondur();
	level notify("savunma_basladi");
	leonov_der("koy_temiz");

	level.player setfriendlychain(getnode("fc4", "targetname"));
	objective_add(2, "active", &"KRASNOYE_OBJ_SAVUNMA", (0, -820, 0));
	objective_current(2);
	level thread leonov_der("savunma");
	t = 0;
	while (level.player.origin[1] > -500 && t < 40)
	{
		wait 0.5;
		t += 0.5;
	}
	objective_state(2, "done");
	autoSaveByName("savunma");

	level thread muzik("krasnoye_muzik_hazirlik");
	objective_add(3, "active", &"KRASNOYE_OBJ_PUSKURT", (-800, -1600, 0));
	objective_current(3);
	wait 6;

	// Kullanici: kamyon + 15 yaya (5 sn'de 5) -> hepsi olunce 5 sn sonra
	// yari paletli + 20 yaya (6 sn'de 5) -> hepsi olunce 5 sn sonra
	// Panzer II + 25 yaya (7 sn'de 5).
	// 1) kamyon + piyade
	leonov_der("kamyon");
	araclar = maps\_vehicle::scripted_spawn(1);
	level thread maps\_vehicle::gopath(araclar[0]);
	araclar[0] thread inenler_saldirsin();
	dalga_dogur("dalga1", 15, 5, 5);
	alman_kalmadi();
	level thread leonov_der("geri_cekiliyor");
	autoSaveByName("dalga1");
	wait 5;

	// 2) yari paletli + piyade
	level thread leonov_der("yaripalet");
	araclar = maps\_vehicle::scripted_spawn(2);
	level thread maps\_vehicle::gopath(araclar[0]);
	araclar[0] thread inenler_saldirsin();
	dalga_dogur("dalga2", 20, 5, 6);
	alman_kalmadi();
	autoSaveByName("dalga2");
	wait 5;

	// 3) SIS + HURRA + Panzer II (demolition savunma acilisi birebir:
	// once 4 sis patlar, Alman "hurra" kalabaligi duyulur, komiser
	// konusur; 3 sn sonra 35 Alman gelmeye baslar; 20'si dogunca 2 sn
	// sonra tank dogar ve Leonov "tank geliyor" der)
	leonov_der("bekle");                        // once Leonov konusur
	sis_patlat();                               // sonra Alman dogus yerlerinde sis
	level thread hurra();
	wait 1;
	level thread dalga_dogur("dalga3", 35, 5, 7, 12, 6);  // 12 birden, 6 sn sonra 5'er
	level waittill("dalga_dogan_20");
	wait 2;
	level thread leonov_der("tank");
	araclar = maps\_vehicle::scripted_spawn(3);
	tank = araclar[0];
	level.tank = tank;
	tank.pos_id = 0;
	tank.grenadetank_dist = 512;
	tank thread tank_explosives();
	level thread maps\_vehicle::gopath(tank);
	tank thread tank_devriye();

	objective_state(3, "done");
	objective_add(4, "active", &"KRASNOYE_OBJ_BOMBA", getent("yapiskan_model", "targetname").origin);
	objective_current(4);
	level thread leonov_der("bomba_al");
	yapiskan_al();
	objective_state(4, "done");
	autoSaveByName("yapiskan");                 // her gorev sonunda kayit

	objective_add(5, "active", &"KRASNOYE_OBJ_TANK", tank.origin);
	objective_current(5);
	level thread tank_yildiz(5, tank);
	level thread leonov_der("bomba_yapistir");
	tank waittill("death");
	flag_set("tank_bitti");
	objective_state(5, "done");
	autoSaveByName("tank");

	// SON SAHNE (kullanici): Alman sayisi 7'ye inince 15 Sovyet takviyesi;
	// 4'e inince kalanlar dogdugu yere kacar ve zafer.
	alman_sayisi_bekle(12);
	level thread son_takviye();
	alman_sayisi_bekle(4);
	level notify("almanlar_kaciyor");
	dusman = getaiarray("axis");
	for (i = 0; i < dusman.size; i++)
		dusman[i] thread alman_kac();

	level thread muzik("krasnoye_muzik_zafer");  // dongude
	leonov_der("zafer");
	iprintlnbold(&"KRASNOYE_BITTI");
	wait 3;                                     // konusma bitti + 3 sn
	bolum_sonu();
}

// dalga dogumu bitmis ve canli Alman sayisi "n" ya da altinda
alman_sayisi_bekle(n)
{
	while (level.dalga_suruyor || getaiarray("axis").size > n)
		wait 0.5;
}

// Almanlarin dogdugu yol koridoru (harita disi, bati)
alman_cikis()
{
	return (-3400, -2040, 0);
}

alman_kac()
{
	self endon("death");
	self notify("kaciyor");
	self.saldiri = undefined;
	self.ignoreme = false;
	self.goalradius = 96;
	self.interval = 0;
	self allowedstances("stand");
	self setgoalpos(alman_cikis());
	self waittill("goal");
	self delete();
}

// 15 Sovyet takviyesi, stok takviyelerin dogdugu kuzey sirt arkasindan
son_takviye()
{
	for (i = 0; i < level.dalga_tetik.size; i++)
		level.dalga_tetik[i] triggerOff();
	sp = getentarray("takviye_kuzey", "targetname");
	for (n = 0; n < 15; n++)
	{
		s = sp[n % sp.size];
		guy = undefined;
		for (deneme = 0; deneme < 20; deneme++)
		{
			s.count = 1;
			guy = s dospawn();
			if (!spawn_failed(guy))
				break;
			wait 0.2;
		}
		if (spawn_failed(guy))
			continue;
		if (n % 2)
			guy thread son_koy();
		else
			guy thread son_avci();
		wait 0.5;
	}
}

// yarisi koye dagilir, siper alir
son_koy()
{
	self endon("death");
	self.goalradius = 200;
	merkez = (-250, 300, 0);
	aday = [];
	for (i = 0; i < level.siper.size; i++)
		if (distance((level.siper[i].origin[0], level.siper[i].origin[1], 0), merkez) < 1200)
			aday[aday.size] = level.siper[i];
	if (aday.size)
		self setgoalnode(aday[randomint(aday.size)]);
	else
		self setgoalpos(merkez);
}

// yarisi kacan Almanlarin pesine duser, oldurur, sonra cikista kaybolur
son_avci()
{
	self endon("death");
	self.goalradius = 400;
	self setgoalpos((-2500, -1950, 0));
	t = 0;
	while (t < 45)
	{
		dusman = getaiarray("axis");
		if (!dusman.size)
			break;
		en = dusman[0];
		for (i = 1; i < dusman.size; i++)
			if (distance(dusman[i].origin, self.origin) < distance(en.origin, self.origin))
				en = dusman[i];
		self.goalradius = 300;
		self setgoalpos(en.origin);
		wait 2;
		t += 2;
	}
	self.goalradius = 96;
	self setgoalpos(alman_cikis());
	self waittill("goal");
	self delete();
}

// Leonov konusmasi bitti: 5 sn'de karar, bolum tamamlanir
bolum_sonu()
{
	perde = newHudElem();
	perde.x = 0;
	perde.y = 0;
	perde.horzAlign = "fullscreen";
	perde.vertAlign = "fullscreen";
	perde.alpha = 0;
	perde setshader("black", 640, 480);
	perde fadeOverTime(6);                      // 6 sn'de kararir
	perde.alpha = 1;
	wait 6.5;
	missionSuccess("metel", false);         // devami: Operatsiya Metel (credits.gsc:1135 kalibi)
}

// tanka tirmanistan 2 sn sonra, TEK SEFER; tank patlamissa calmaz
tank_muzik(tank)
{
	if (isdefined(level.tank_muzik_caldi))
		return;
	level.tank_muzik_caldi = true;
	tank endon("death");
	wait 0.5;
	if (!isalive(tank) && !isdefined(tank.vehicle_disabled))
		return;
	level thread muzik("krasnoye_muzik_tank");
}

muzik_sondur()
{
	level notify("muzik_degisti");
	musicstop(3);
}

// demolition smokeGen/throwSmoke: 4 sis tank yolunun koy agzina
sis_patlat()
{
	sp = getentarray("dalga3", "targetname");
	atan = level.leonov;
	for (i = 0; i < 4; i++)
	{
		p = sp[int(i * (sp.size - 1) / 3)].origin;
		tr = bulletTrace(p + (0, 0, 400), p - (0, 0, 800), false, undefined);
		yer = tr["position"];
		eski = atan.grenadeWeapon;
		atan.grenadeWeapon = "smoke_grenade_american";
		atan.grenadeAmmo++;
		atan MagicGrenade(yer + (0, 0, 50), yer, 0.5);
		atan.grenadeWeapon = eski;
		wait (0.4 + randomfloat(0.4));
	}
}

// demolition exploder 51 "german Walla": sisin arkasindan hurra kalabaligi
hurra()
{
	// dogus yerinde kalabalik + oyuncuya dogru katman (yuksek duyulsun)
	org = spawn("script_origin", (-3200, -2050, 80));
	org2 = spawn("script_origin", (-1800, -1800, 80));
	org playsound("walla_german_large", "sounddone");
	org2 playsound("walla_german_large_layer");
	org waittill("sounddone");
	org delete();
	org2 delete();
}

// parca gecisi: stok demolition music_awaitingattack gibi once sondur
muzik(alias)
{
	level notify("muzik_degisti");
	level endon("muzik_degisti");
	musicstop(2);
	wait 2.1;
	musicplay(alias);
}

// demolition.gsc music_tensionfragments() birebir: 3-8 sn sonra
muzik_giris()
{
	wait randomfloatrange(3, 8);
	musicplay("krasnoye_muzik_giris");
}

// toplam kadar asker, her "aralik" saniyede "parti" kadar (harita disi
// orman kenari spawner'lari; dospawn gorulurse basarisiz -> tekrar dener)
dalga_dogur(ad, toplam, parti, aralik, ilk, ilk_bekle)
{
	level.dalga_suruyor = true;
	sp = getentarray(ad, "targetname");
	// g_connectpaths olcumu: (-3333,-1970) spawner'i kati icinde -> kullanma
	temiz = [];
	for (i = 0; i < sp.size; i++)
	{
		if (distance((sp[i].origin[0], sp[i].origin[1], 0), (-3333, -1970, 0)) < 40)
			sp[i] delete();
		else
			temiz[temiz.size] = sp[i];
	}
	sp = temiz;
	dogan = 0;
	bu = parti;
	if (isdefined(ilk))
		bu = ilk;
	while (dogan < toplam)
	{
		for (i = 0; i < bu && dogan + i < toplam; i++)
		{
			s = sp[i % sp.size];
			guy = undefined;
			for (deneme = 0; deneme < 15; deneme++)
			{
				s.count = 1;
				guy = s dospawn();
				if (!spawn_failed(guy))
					break;
				wait 0.2;
			}
			if (spawn_failed(guy))
			{
				s.count = 1;
				guy = s stalingradspawn();
			}
			if (!spawn_failed(guy))
				guy thread saldirgan();
		}
		onceki = dogan;
		dogan += bu;
		if (dogan > toplam)
			dogan = toplam;
		for (k = onceki + 1; k <= dogan; k++)
			level notify("dalga_dogan_" + k);
		if (dogan < toplam)
		{
			if (bu != parti && isdefined(ilk_bekle))
				wait ilk_bekle;
			else
				wait aralik;
		}
		bu = parti;
	}
	for (i = 0; i < sp.size; i++)
		if (isdefined(sp[i]))
			sp[i] delete();
	level.dalga_suruyor = false;
}

// dalga dogumu bitti VE canli Alman kalmadi
alman_kalmadi()
{
	wait 1;
	while (level.dalga_suruyor || getaiarray("axis").size > 0)
		wait 1;
}

// aractan inenler: arac durup inis animasyonu bitince saldiriya gecer
inenler_saldirsin()
{
	self waittill("reached_end_node");
	wait 5;
	if (!isdefined(self.riders))
		return;
	for (i = 0; i < self.riders.size; i++)
		if (isalive(self.riders[i]) && issentient(self.riders[i]))
			self.riders[i] thread saldirgan();
}

// tum siper dugumleri bir kez okunur (stok _load/_spawner getallnodes)
siper_onbellek()
{
	level.siper = [];
	nodes = getallnodes();
	for (i = 0; i < nodes.size; i++)
		if (issubstr(nodes[i].type, "Cover"))
			level.siper[level.siper.size] = nodes[i];
}

// hedef noktaya en yakin, oyuncuya en az "min" uzak siper dugumu
siper_bul(hedef, en_cok, min)
{
	en = undefined;
	ed = en_cok;
	for (i = 0; i < level.siper.size; i++)
	{
		n = level.siper[i];
		d = distance(n.origin, hedef);
		if (d < ed && distance(n.origin, level.player.origin) > min)
		{
			en = n;
			ed = d;
		}
	}
	return en;
}

// SALDIRAN ALMAN: oyuncuya dogru siperden sipere atilir (her adim en fazla
// ~550 birim), hedef yakininda siper alir, ates eder, sonra tekrar ilerler.
saldirgan()
{
	self endon("death");
	self endon("kaciyor");
	self.saldiri = true;
	wait randomfloatrange(0.5, 2);
	for (;;)
	{
		p = level.player.origin;
		d = distance(self.origin, p);
		if (d < 450)
		{
			self.goalradius = 320;
			self setgoalpos(p);
			wait randomfloatrange(4, 7);
			continue;
		}
		adim = d - 300;
		if (adim > 550)
			adim = 550;
		hedef = self.origin + vectorScale(vectornormalize(p - self.origin), adim);
		n = siper_bul(hedef, 400, 250);
		if (isdefined(n))
		{
			self.goalradius = 96;
			self setgoalnode(n);
		}
		else
		{
			self.goalradius = 256;
			self setgoalpos(hedef);
		}
		self hedef_bekle(12);
		wait randomfloatrange(3, 7);              // siperde ates
	}
}

// "goal" gelene ya da sure dolana kadar bekler
hedef_bekle(sure)
{
	self endon("goal");
	wait sure;
}

spawner_sil(ad)
{
	sp = getentarray(ad, "targetname");
	for (i = 0; i < sp.size; i++)
		if (isdefined(sp[i]) && !isalive(sp[i]))
			sp[i] delete();
}

// KOY SAVUNUCUSU: sabit durmaz. Koy icindeki siperler arasinda yer
// degistirir; oyuncu yaklasinca geri cekilip baska sipere kacar, uzaktaysa
// yan siperlere kayarak pozisyon degistirir.
koy_savunucu()
{
	self endon("death");
	self endon("kaciyor");
	merkez = (-250, 300, 0);
	wait randomfloatrange(3, 8);
	for (;;)
	{
		p = level.player.origin;
		yakin = distance(self.origin, p) < 600;
		aday = [];
		for (i = 0; i < level.siper.size; i++)
		{
			n = level.siper[i];
			if (distance((n.origin[0], n.origin[1], 0), merkez) > 1500)
				continue;
			dn = distance(n.origin, self.origin);
			if (dn < 120 || dn > 750)
				continue;
			if (distance(n.origin, p) < 350)
				continue;
			if (yakin && distance(n.origin, p) < distance(self.origin, p))
				continue;                       // kacarken oyuncuya yaklasma
			aday[aday.size] = n;
		}
		if (aday.size)
		{
			self.goalradius = 96;
			self setgoalnode(aday[randomint(aday.size)]);
			self hedef_bekle(10);
		}
		if (yakin)
			wait randomfloatrange(2, 4);
		else
			wait randomfloatrange(7, 15);
	}
}

// GERIDE KALAN DOST: 20 sn boyunca yerinden kipirdamayan ve oyuncudan
// 1400+ uzak dost, oyuncunun GORMEDIGI yakin bir sipere alinir.
dost_bekcisi()
{
	level waittill("daire_bitti");
	for (;;)
	{
		wait 4;
		dost = getaiarray("allies");
		for (i = 0; i < dost.size; i++)
		{
			g = dost[i];
			if (!isdefined(g.bekci_yer) || distance(g.origin, g.bekci_yer) > 64)
			{
				g.bekci_yer = g.origin;
				g.bekci_sure = 0;
				continue;
			}
			g.bekci_sure += 4;
			if (g.bekci_sure < 20 || distance(g.origin, level.player.origin) < 1400)
				continue;
			n = dost_gizli_dugum();
			if (!isdefined(n))
				continue;
			g teleport(n.origin);
			friendlyMethod(g);
			g.bekci_yer = n.origin;
			g.bekci_sure = 0;
		}
	}
}

dost_gizli_dugum()
{
	goz = level.player geteye();
	for (i = 0; i < level.siper.size; i++)
	{
		n = level.siper[i];
		d = distance(n.origin, level.player.origin);
		if (d < 350 || d > 900)
			continue;
		if (sighttracepassed(goz, n.origin + (0, 0, 40), false, undefined))
			continue;
		return n;
	}
	return undefined;
}

dalga_bekle(grup, sure)
{
	level endon("dalga_bitti_" + grup);
	level thread dalga_sure(grup, sure);
	waittill_aigroupcleared(grup);
	level notify("dalga_bitti_" + grup);
}

dalga_sure(grup, sure)
{
	level endon("dalga_bitti_" + grup);
	wait sure;
	level notify("dalga_bitti_" + grup);
}

// Tank koyde 5 noktalik dongu devriyesi (yol zinciri harita tarafinda
// kapali halka). Her durakta 7-14 sn bekler, sonra devam eder. Stok
// _vehicle.gsc vehicle_setspeed / script_resumespeed sarmalayicilari.
tank_devriye()
{
	self endon("death");
	self endon("disabled");
	self thread tank_duraklar();
	self waittill("reached_end_node");          // ana yol A noktasinda biter
	for (;;)
	{
		wait 0.5;
		self connectpaths();
		self attachpath(getvehiclenode("tank_dongu", "targetname"));
		self startpath();
		self maps\_vehicle::vehicle_setspeed(3, 5, "devriye");
		self waittill("reached_end_node");
	}
}

// Her durakta 7-14 sn bekle (kullanici istegi)
tank_duraklar()
{
	self endon("death");
	self endon("disabled");
	duraklar = getentarray("tank_durak", "targetname");
	son = undefined;
	for (;;)
	{
		wait 0.2;
		for (i = 0; i < duraklar.size; i++)
		{
			if (isdefined(son) && son == duraklar[i])
				continue;
			if (distance((self.origin[0], self.origin[1], 0), (duraklar[i].origin[0], duraklar[i].origin[1], 0)) > 140)
				continue;
			son = duraklar[i];
			self maps\_vehicle::vehicle_setspeed(0, 15, "devriye duragi");
			wait randomfloatrange(7, 14);
			if (isdefined(self.vehicle_disabled))
				return;
			self maps\_vehicle::vehicle_setspeed(3, 5, "devriye devam");
			break;
		}
	}
}

tank_yildiz(no, tank)
{
	tank endon("death");
	for (;;)
	{
		objective_position(no, tank.origin);
		wait 0.1;
	}
}

// tankhunt get_sticky_bombs() kalibi
yapiskan_al()
{
	trig = getent("yapiskan_al", "targetname");
	getent("yapiskan_model", "targetname") show();
	trig triggerOn();
	trig sethintstring(&"TANKHUNT_PLATFORM_PICK_UP_STICKY_BOMBS");
	trig waittill("trigger");
	m = getent("yapiskan_model", "targetname");
	if (isdefined(m))
		m delete();
	level.player playsound("stickybomb_plant");
	trig delete();
	level.inv_sticky = maps\_inventory::inventory_create("inventory_stickybomb", true);
	level.player.stickybomb = 3;
	flag_set("yapiskan_alindi");
}

// ==========================================================================
// YAPISKAN BOMBA + TANK YANASMA SAHNESI -- tankhunt.gsc birebir port
// ==========================================================================
tank_explosives()
{
	self endon ("death");
	self thread tank_ondeath();
	self.bombTriggers = [];
	self.bombs = [];
	tags = [];
	tags[0] = "tag_engine_left";
	tags[1] = "tag_left_wheel_07";
	tags[2] = "tag_right_wheel_07";
	location_angles = [];
	location_angles[0] = (0,70,-90);
	location_angles[1] = (0,-90,0);
	location_angles[2] = (0,90,0);
	for (i=0; i < tags.size; i++)
	{
		bomb = spawn("script_model", self gettagorigin(tags[i]));
		bomb setmodel("xmodel/weapon_stickybomb_obj");
		bomb.angles = location_angles[i];
		bomb linkto(self,tags[i]);
		bomb.trigger = undefined;
		aTrigger = getentarray("sticky_trigger","targetname");
		for (t=0; t < aTrigger.size; t++)
		{
			if (!isdefined(aTrigger[t].inuse))
			{
				bomb.trigger = aTrigger[t];
				break;
			}
		}
		bomb.trigger.inuse = true;
		bomb.tanktag = tags[i];
		bomb.trigger.oldorigin = bomb.trigger.origin;
		bomb.trigger.origin = bomb.origin;
		if (!isdefined(bomb.trigger.linktoenable))
			bomb.trigger enablelinkto();
		bomb.trigger.linktoenable = true;
		bomb.trigger linkto(bomb);
		self.bombs[i] = bomb;
		self thread tank_explosives_wait(bomb.trigger,i);
	}
	self waittill ("explosives planted",id);
	badplacename = ("tank_badplace_" + randomfloat(1000));
	badplace_cylinder(badplacename, -1, self.origin, 250, 300);
	iprintlnbold (&"SCRIPT_EXPLOSIVESPLANTED");
	level notify("sticky planted");
	bomb = self.bombs[id];
	remove_stickys(self.bombs,id);
	bomb setmodel ("xmodel/weapon_stickybomb");
	bomb playsound ("stickybomb_plant");
	bomb playloopsound ("bomb_tick");
	level stopwatch(bomb);
	badplace_delete(badplacename);
	if (id == 0)
	{
		bomb.trigger.inuse = undefined;
		bomb delete();
		self notify ("death", level.player);
	}
	else
	{
		self setspeed(0,25,"Dead");
		if (bomb.tanktag == "tag_right_wheel_07")
			self setmodel("xmodel/vehicle_panzer_ii_winter_r_tread_d");
		else
			self setmodel("xmodel/vehicle_panzer_ii_winter_l_tread_d");
		self disconnectpaths();
		self.vehicle_disabled = true;
		self playsound ("grenade_explode_default");
		playfx(level._effect["sticky_explosion"], bomb.origin);
		explosion_origin = bomb.origin;
		bomb.trigger.inuse = undefined;
		bomb delete();
		nocover_radiusdamage(explosion_origin, 200, 300, 50);
		if (isdefined(level.runupactive) && level.runupactive)
		{
			wait 2;
			self notify ("death", level.player);
		}
		else
		{
			self notify("disabled");
			self tank_runup();
		}
	}
}

remove_stickys(bombs, id)
{
	if (!isdefined(id))
		id = 1000;
	for (i=0;i < bombs.size;i++)
	{
		if (!isdefined(bombs[i]))
			continue;
		if (i != id)
		{
			bombs[i].trigger unlink();
			bombs[i].trigger.inuse = undefined;
			bombs[i].trigger.origin = bombs[i].trigger.oldorigin;
			bombs[i] delete();
		}
		else
		{
			bombs[i].trigger unlink();
			bombs[i].trigger.origin = bombs[i].trigger.oldorigin;
		}
	}
}

tank_runup_guys(origin)
{
	aAI = getaiarray("allies");
	aGuys = [];
	aGuys[0] = undefined;
	aGuys[1] = undefined;
	for (i=0; i<aAi.size; i++)
	{
		if (isdefined(level.leonov) && aAi[i] == level.leonov)
			continue;
		dist = distance(origin,aAi[i].origin);
		if (!isdefined(aGuys[0]))
			aGuys[0] = aAi[i];
		else if (dist < distance(origin,aGuys[0].origin))
		{
			aGuys[1] = aGuys[0];
			aGuys[0] = aAi[i];
		}
		else if (!isdefined(aGuys[1]))
			aGuys[1] = aAi[i];
		else if (dist < distance(origin,aGuys[1].origin))
			aGuys[1] = aAi[i];
	}
	return aGuys;
}

tank_runup()
{
	self endon("death");
	timer = 0;
	while (true)
	{
		german = getclosestai(self.origin,"axis");
		if (!isdefined(german))
			break;
		else if (distance(self.origin,german.origin) > self.grenadetank_dist)
			break;
		if (timer > 20)
			break;
		timer++;
		wait .5;
	}
	aAi = tank_runup_guys(self.origin);
	runupguy = aAi[0];
	gunguy = aAi[1];
	if (!isdefined(runupguy) || isdefined(level.runupactive) && level.runupactive)
	{
		wait 2;
		self notify ("death", level.player);
		return;
	}
	level.runupactive = true;
	runupguy thread runupguy_animation(self,gunguy);
	if (isdefined(gunguy))
		gunguy thread gunguy_animation(self,runupguy);
	self thread runup_guy_stuck(runupguy,gunguy);
	self notify("stop cycle");
	self clearturrettarget();
	offset = angleoffset(self.angles, (100000,0,0));
	self setturrettargetent(self, offset);
}

runupguy_animation(tank,gunguy)
{
	tank endon("death");
	self.atgoal = undefined;
	self.animname = "runupguy";
	self.ignoreme = true;
	self.old_maxsightdistsqrd = self.maxsightdistsqrd;
	self.maxsightdistsqrd = (256*256);
	self.old_pathenemyfightdist = self.pathenemyfightdist;
	self.pathenemyfightdist = 64;
	self clearEnemyPassthrough();
	self thread magic_bullet_shield();
	self anim_reach_solo (self, "grenadetank", "tag_origin", undefined, tank);
	self.atgoal = true;
	self notify("climb anim started");
	switch(level.runups)
	{
		case 1:
			self thread Dialogue_Thread("demolition_rs4_motherrussia");
			break;
		case 2:
			self thread Dialogue_Thread("commissar_charge_attack");
			break;
		default:
			self thread Dialogue_Thread("commissar_charge_killfascists");
			break;
	}
	level.runups++;
	level thread tank_muzik(tank);
	if ( isdefined(gunguy) && !isdefined(gunguy.atgoal) && !isdefined(self.noclimb) )
	{
		self anim_single_solo(self, "grenadetank", "tag_origin", undefined, tank);
		self thread anim_loop_solo (self, "grenadetank_loop", "tag_origin", "end_loop", undefined, tank);
		if ( isdefined(gunguy) && isalive(gunguy) )
			gunguy on_location();
		self notify("end_loop");
	}
	else
		self anim_single_solo(self, "grenadetank", "tag_origin", undefined, tank);
	tank thread hatch();
	self notify("end_loop");
	if ( randomint(2) )
		self thread Dialogue_Thread("moscow_rs3_fireinthehole");
	self anim_single_solo(self, "grenadetank_run","tag_origin",undefined,tank);
	self notify("stop magic bullet shield");
	self.ignoreme = false;
	self.maxsightdistsqrd = self.old_maxsightdistsqrd;
	self.pathenemyfightdist = self.old_pathenemyfightdist;
	if (isalive(self))
		self thread friendlyMethod();
	badplace_cylinder("", 4, self.origin, 350, 350, "allies","axis");
	wait 3.5;
	level.runupactive = false;
	tank notify ("death", level.player);
}

gunguy_animation(tank,runupguy)
{
	tank endon("death");
	self endon("gunguy timeout");
	self endon("death");
	self.atgoal = undefined;
	self.animname = "gunguy";
	self.ignoreme = true;
	self.old_maxsightdistsqrd = self.maxsightdistsqrd;
	self.maxsightdistsqrd = (256*256);
	self.old_pathenemyfightdist = self.pathenemyfightdist;
	self.pathenemyfightdist = 64;
	self clearEnemyPassthrough();
	self thread magic_bullet_shield();
	wait 1;
	self anim_reach_solo (self, "grenadetank", "tag_origin", undefined, tank);
	if (!isdefined(runupguy.atgoal))
	{
		self.noclimb = true;
		self notify("stop magic bullet shield");
		self.ignoreme = false;
		self.maxsightdistsqrd = self.old_maxsightdistsqrd;
		self.pathenemyfightdist = self.old_pathenemyfightdist;
		self thread friendlyMethod();
		return;
	}
	self.atgoal = true;
	self notify("climb anim started");
	self anim_single_solo(self, "grenadetank","tag_origin", undefined, tank);
	self.animdone = true;
	self notify("climb anim done");
	tank thread hatch();
	self anim_single_solo(self, "grenadetank_run","tag_origin", undefined, tank);
	self notify("stop magic bullet shield");
	self.ignoreme = false;
	self.maxsightdistsqrd = self.old_maxsightdistsqrd;
	self.pathenemyfightdist = self.old_pathenemyfightdist;
	if (isalive(self))
		self thread friendlyMethod();
}

on_location()
{
	self endon("death");
	self endon("gunguy timeout");
	if (!isdefined(self.atgoal))
		self thread time_out();
	if (!isdefined(self.animdone))
		self waittill("climb anim done");
}

time_out()
{
	self endon("death");
	self endon("climb anim started");
	self endon("climb anim done");
	wait 2;
	self notify("gunguy timeout");
	self notify("stop magic bullet shield");
	self.ignoreme = false;
	self.maxsightdistsqrd = self.old_maxsightdistsqrd;
	self.pathenemyfightdist = self.old_pathenemyfightdist;
	self thread friendlyMethod();
}

runup_guy_stuck(runupguy,gunguy)
{
	runupguy endon("climb anim started");
	oldpos = runupguy.origin;
	oks = 0;
	for(i=0;i<5;i++)
	{
		wait 1;
		dif = distance(runupguy.origin, oldpos);
		if (dif > 64)
			oks++;
		oldpos = runupguy.origin;
	}
	if (oks > 1)
		wait 5;
	level.runupactive = false;
	self notify ("death", level.player);
	if (isalive(runupguy))
	{
		runupguy notify("stop magic bullet shield");
		runupguy.ignoreme = false;
		runupguy.maxsightdistsqrd = runupguy.old_maxsightdistsqrd;
		runupguy.pathenemyfightdist = runupguy.old_pathenemyfightdist;
		runupguy thread friendlyMethod();
	}
	if (isdefined(gunguy) && isalive(gunguy))
	{
		gunguy notify("stop magic bullet shield");
		gunguy.ignoreme = false;
		gunguy.maxsightdistsqrd = gunguy.old_maxsightdistsqrd;
		gunguy.pathenemyfightdist = gunguy.old_pathenemyfightdist;
		gunguy thread friendlyMethod();
	}
}

#using_animtree ("tank");
hatch()
{
	self UseAnimTree(#animtree);
	self setanim(%panzertank2_tankhatchanim_grenadeguy);
}
#using_animtree ("generic_human");

tank_explosives_wait(trigger,id)
{
	self endon ("death");
	self endon ("explosives planted");
	trigger setHintString (&"TANKHUNT_PLATFORM_PLANT_STICKY_BOMB");
	while(true)
	{
		trigger waittill ("trigger");
		if (level.player.stickybomb <= 0)
			continue;
		level.player.stickybomb--;
		if (level.player.stickybomb <= 0)
			level.inv_sticky maps\_inventory::inventory_destroy();
		level notify ("explosives planted");
		self notify ("explosives planted", id);
		return;
	}
}

stopwatch(bomb)
{
	if (isdefined (self.bombstopwatch))
		self.bombstopwatch destroy();
	self.bombstopwatch = maps\_utility::getstopwatch(60);
	level.timersused++;
	wait level.explosiveplanttime;
	bomb stoploopsound ("bomb_tick");
	level.timersused--;
	if (level.timersused < 1)
	{
		if (isdefined (self.bombstopwatch))
			self.bombstopwatch destroy();
	}
}

tank_ondeath()
{
	self waittill("death");
	level thread remove_stickys(self.bombs);
	level notify("tank destroyed",self.pos_id);
}

nocover_radiusdamage(org, rad, max, min)
{
	max = max - min;
	ai = getaiarray ();
	for (i=0;i<ai.size;i++)
	{
		dist = distance (org, ai[i].origin);
		if (dist > rad)
			continue;
		ai[i] DoDamage (max * (1 - (dist/rad)) + min, org);
	}
	dist = distance (org, level.player.origin);
	if (dist > rad)
		return;
	level.player DoDamage (max * (1 - (dist/rad)) + min, org);
}

Dialogue_Thread(dialogue,node)
{
	self endon("death");
	if ( isdefined (self.MyIsSpeaking) && self.MyIsSpeaking )
		self waittill ("my done speaking");
	self.MyIsSpeaking = true;
	self setBattleChatter(false);
	self anim_single_solo(self, dialogue);
	self setBattleChatter(true);
	self.MyIsSpeaking = false;
	self notify ("my done speaking");
}

angleoffset(vAngles, vOffset)
{
	vf = anglestoforward(vAngles);
	vr = anglestoright(vAngles);
	vu = anglestoup(vAngles);
	offset_front = vectorscale(vf,vOffset[0]);
	offset_right = vectorscale(vr,(vOffset[1]*-1));
	offset_top = vectorscale(vu,vOffset[2]);
	return offset_right+offset_front+offset_top;
}

// ==========================================================================
// GELISTIRICI: ekran turu (kr_tur 1)
// ==========================================================================
ekran_turu()
{
	level.player takeallweapons();
	nokta = [];
	aci = [];
	nokta[nokta.size] = (0, 1880, 70);       aci[aci.size] = (8, 270, 0);
	nokta[nokta.size] = (-2200, 2200, 900);  aci[aci.size] = (35, 315, 0);
	nokta[nokta.size] = (0, 300, 1700);      aci[aci.size] = (89, 270, 0);
	nokta[nokta.size] = (-250, -700, 70);    aci[aci.size] = (5, 90, 0);
	nokta[nokta.size] = (0, -900, 70);       aci[aci.size] = (5, 270, 0);
	nokta[nokta.size] = (0, -2900, 400);     aci[aci.size] = (12, 90, 0);
	nokta[nokta.size] = (-1100, 700, 70);    aci[aci.size] = (5, 0, 0);
	nokta[nokta.size] = (0, 2900, 70);       aci[aci.size] = (5, 270, 0);
	nokta[nokta.size] = (0, 900, 2450);      aci[aci.size] = (89, 90, 0);
	nokta[nokta.size] = (-700, -1500, 2450); aci[aci.size] = (89, 90, 0);
	nokta[nokta.size] = (60, 640, 90);       aci[aci.size] = (5, 75, 0);
	nokta[nokta.size] = (-250, -150, 110);   aci[aci.size] = (10, 30, 0);
	nokta[nokta.size] = (-500, -1000, 90);   aci[aci.size] = (3, 200, 0);
	nokta[nokta.size] = (950, 300, 110);     aci[aci.size] = (10, 140, 0);
	if (getcvar("kr_tur") == "2")
	{
		nokta = [];
		aci = [];
		nokta[nokta.size] = (0, 0, 2500);       aci[aci.size] = (89, 90, 0);
		nokta[nokta.size] = (0, 1400, 2450);    aci[aci.size] = (89, 90, 0);
		nokta[nokta.size] = (-600, -1600, 2450); aci[aci.size] = (89, 90, 0);
		nokta[nokta.size] = (-2600, 3200, 1600); aci[aci.size] = (35, 315, 0);
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

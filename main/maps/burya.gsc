// burya.gsc -- "Operation Snowstorm / Kar Firtinasi", 2 Subat 1943 (metel'in devami).
//
// AKIS (senaryo + kullanici oyun testi kararlari, 22 Ekim):
//   1) KONVOY: oyuncu 2. kamyonun kasasinda (stok beltot tag_player kalibi),
//      Leonov + 4 asker kasada; kamyonlar perde acilmadan once kalkar.
//   2) PUSU: arkadaki kamyon kopru ustunde mayina basar (yolculari olur, geri
//      donus kapanir), ondeki kamyon saga kirip durur; 10 Alman ormandan gelir.
//   3) KAMP GIRISI: 10 + 2 MG42 (kulede yatarak dogar, kalkip MG'ye gecer ve
//      MG'yi BIRAKMAZ). Takviye gelene kadar (inisten 60 sn sonra, tek kamyon)
//      olen her Alman 2-5 sn sonra kampin icinde, gorulmeyen yerde yeniden doger.
//   4) Takviye geldikten sonra bir Sovyet kampa girince dis dogus durur; kamp
//      ici 15 + merkez 7 + bina ici yedekler (binalar, bomba odalari).
//   5) KARSI SALDIRI: 50 Alman, 5-6 sn'de 5-6, ormandan her yonden. Sovyetler
//      siper alir, ikisi el merdiveninden kulelere cikip MG42'leri kullanir.
//   6) BOMBA: 3 patlayici; hepsi kurulunca 20 sn sayac (muzik 15. sn'de),
//      Sovyetler kampi terk edip disarida comelerek izler.
//   7) 3 AYRI PATLAMA: baraka, depo, merkez bina yikilir; kuleler devrilir;
//      kamptaki her canli olur; giris enkazla kapanir. Leonov'un sozleri.
// Kaliplar: beltot (oyuncu kamyonda), decoytown (kamyondan inme), rhine
// (araci patlatma), demolition (TNT, bina yikimi), _bombs (kronometre),
// _spawner use_a_turret (MG42), tankhunt (ladder_up negotiation), metel.
#include maps\_utility;
#include maps\_anim;

main()
{
	setExpFog(0.00025, .64, .68, .74, 0);
	setCullDist(12000);

	precacheString(&"BURYA_OBJ_KONVOY");
	precacheString(&"BURYA_OBJ_PUSU");
	precacheString(&"BURYA_OBJ_KAMP");
	precacheString(&"BURYA_OBJ_GIRIS");
	precacheString(&"BURYA_OBJ_SAVUN");
	precacheString(&"BURYA_OBJ_ELE");
	precacheString(&"BURYA_OBJ_BEKLE");
	precacheString(&"BURYA_OBJ_BOMBA");
	precacheString(&"BURYA_OBJ_KAC");
	precacheString(&"BURYA_OBJ_LEONOV");
	precacheString(&"BURYA_MSG_TAKVIYE");
	precacheString(&"BURYA_BITTI");
	precacheString(&"BURYA_INTRO_TITLE");
	precacheString(&"BURYA_INTRO_PLACE");
	precacheString(&"BURYA_INTRO_DATE");
	precacheString(&"BURYA_INTRO_INFO");
	precacheString(&"BURYA_PLATFORM_BOMBA_KUR");
	precacheShader("black");
	precacheShader("hudStopwatch");
	precacheShader("hudStopwatchNeedle");
	precacheModel("xmodel/military_tntbomb");
	precacheModel("xmodel/military_tntbomb_obj");
	precacheModel("xmodel/gully_bridge_debris_sm01");
	precacheModel("xmodel/gully_bridge_debris_sm02");
	precacheModel("xmodel/gully_bridge_debris_sm03");
	precacheModel("xmodel/moscow_boards_1a");
	precacheModel("xmodel/moscow_boards_2b");
	precacheModel("xmodel/vehicle_opel_blitz_woodland_d_static");

	level.campaign = "russian";
	level.totalfriends = 0;                     // _load'dan ONCE (krasnoye olcusu)
	level.maxfriendlies = 0;
	maps\_truck::main("xmodel/vehicle_opel_blitz_snow");
	maps\burya_fx::main();
	maps\_load::main();
	maps\burya_anim::main();

	level.friendlyMethod = "friendly chains";
	// friendly chain kullanilmiyor (ekip betikle yonetilir)
	level.ekip_mod = "bekle";
	level.hucum_siper = [];

	flag_init("konvoy_vuruldu");
	flag_init("indik");
	flag_init("pusu_temiz");
	flag_init("takviye_indi");
	flag_init("sovyet_kampta");
	flag_init("kamp_temiz");
	flag_init("karsi_bitti");
	flag_init("bomba_kuruldu");
	flag_init("patladi");
	flag_init("bitti");
	flag_init("ic_dogdu");
	flag_init("kalk");
	flag_init("tanitim_bitti");

	level.sinir = maps\burya_sinir::cokgen();
	// derlemede uzakta duran brushmodel'ler (yol agi dersi) yerine konur
	level.bina_saglam = getent("bina_saglam", "targetname");
	level.bina_saglam moveto(level.bina_saglam.origin + (9000, 0, 0 - 2000), 0.05);
	level.bina_yikik = getent("bina_yikik", "targetname");
	level.bina_yikik hide();                    // +2000'de; patlamada inip gorunur
	level.bina_yikik notsolid();
	level.yikilir = [];
	level.yikik = [];
	ad = [];
	ad[0] = "baraka_a";
	ad[1] = "depo_a";
	ad[2] = "baraka_b";
	ad[3] = "baraka_c";
	ad[4] = "baraka_d";
	ad[5] = "depo_b";
	for (i = 0; i < ad.size; i++)
	{
		e = getent("yikilir_" + ad[i], "targetname");
		e moveto(e.origin + (9216, 0, 0), 0.05);
		level.yikilir[ad[i]] = e;
		y = getent("yikik_" + ad[i], "targetname");
		y hide();
		y notsolid();
		level.yikik[ad[i]] = y;
	}
	// kullanici: bomba yerleri bomba gorevine kadar gorunmez/kullanilmaz
	b = getentarray("bomba", "targetname");
	for (i = 0; i < b.size; i++)
	{
		b[i] hide();
		t = getent(b[i].target, "targetname");
		t.eski_yer = t.origin;
		t.origin = t.origin + (0, 0, 0 - 10000);
	}
	level.kapi_enkaz = getent("kapi_enkaz", "targetname");
	level.kapi_enkaz hide();
	level.kapi_enkaz notsolid();
	level.patlama_yeri = getent("patlama", "targetname").origin;
	level.kamp_kapi = getent("kamp_kapi", "targetname").origin;
	level.guvenli = getent("guvenli", "targetname").origin;
	level.kamp_orta = (2950, 2250, 40);

	if (getcvar("kr_tur") != "" && getcvar("kr_tur") != "0")
	{
		level thread ekran_turu();
		return;
	}

	oyuncu_techizat();
	siper_onbellek();
	anim.noWeaponToss = true;
	level.sovyetler = [];
	level thread ekip_beyni();
	level thread gorevler();
	if (getcvar("kr_test") == "1")
		level thread otomatik_test();
}

// --------------------------------------------------------------------------
// TANITIM: siyah perde 3 sn'de acilir. Kullanici: kamyonlar perde bitmeden
// once harekete gecsin -> kalkis emri perdeden 2 sn once (ivmelenme payi).
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
	musicplay("burya_muzik_giris");
	wait .05;
	level.introstring = [];
	maps\_introscreen::introscreen_create_line(&"BURYA_INTRO_TITLE");
	wait 2;
	maps\_introscreen::introscreen_create_line(&"BURYA_INTRO_PLACE");
	maps\_introscreen::introscreen_create_line(&"BURYA_INTRO_DATE");
	wait 2;
	maps\_introscreen::introscreen_create_line(&"BURYA_INTRO_INFO");
	wait 1;
	flag_set("kalk");                           // kullanici: araclar perde bitmeden 2 sn once hareketli
	wait 2;
	level notify("perde_aciliyor");
	level.introblack fadeOverTime(3);
	level.introblack.alpha = 0;
	maps\_introscreen::introscreen_fadeOutText();
	flag_set("tanitim_bitti");
}

// senaryo: Mosin + PPSh (baska silah yok); 4 el bombasi, 2 duman
oyuncu_techizat()
{
	level.player takeallweapons();
	level.player giveWeapon("mosin_nagant");
	level.player giveWeapon("ppsh");
	level.player giveWeapon("RGD-33russianfrag");
	level.player giveWeapon("smoke_grenade_russian");
	level.player giveMaxAmmo("mosin_nagant");
	level.player giveMaxAmmo("ppsh");
	level.player setWeaponClipAmmo("RGD-33russianfrag", 4);
	level.player setWeaponClipAmmo("smoke_grenade_russian", 2);
	level.player switchToWeapon("mosin_nagant");
	level.player switchToOffhand("RGD-33russianfrag");
	maps\_loadout::setup_russian();
}

// --------------------------------------------------------------------------
// GOREV AKISI (asamalar senaryodaki adlarla: level.asama)
// --------------------------------------------------------------------------
gorevler()
{
	level thread tanitim();
	level.asama = "CONVOY_MOVING";
	objective_add(1, "active", &"BURYA_OBJ_KONVOY", level.kamp_kapi);
	objective_current(1);
	level thread konvoy();
	flag_wait("konvoy_vuruldu");

	// --- PUSU
	level.asama = "CONVOY_AMBUSH";
	objective_state(1, "done");
	objective_add(2, "active", &"BURYA_OBJ_PUSU", level.patlama_yeri);
	objective_current(2);
	level thread muzik("burya_muzik_pusu");
	flag_wait("indik");
	tum = tum_sovyetler();
	for (i = 0; i < tum.size; i++)
		tum[i] thread takili_kurtar();              // kullanici: Leonov/asker kamyon basinda kaliyordu
	level thread takviye_zamanla();             // kullanici: inisten 60 sn sonra
	level.asama = "FIRST_ENCOUNTER";
	level thread leonov_der("pusu");
	ekip_hucum(level.patlama_yeri, 900);
	waittill_aigroupcleared("pusu");
	flag_set("pusu_temiz");
	for (i = 0; i < level.sovyetler.size; i++)
	{
		g = level.sovyetler[i];
		if (!isalive(g))
			continue;
		g notify("yeni_emir");
		g.ekip_uyesi = true;
		level.ekip[level.ekip.size] = g;
	}
	level.sovyetler = [];
	objective_state(2, "done");
	level thread autoSaveByName("pusu_bitti");

	// --- KAMPA ILERLE
	level.asama = "ADVANCE_TO_CAMP";
	level.ekip_mod = "takip";
	level thread muzik("burya_muzik_yolculuk");
	leonov_der("ilerle");
	objective_add(3, "active", &"BURYA_OBJ_KAMP", level.kamp_kapi);
	objective_current(3);
	while (distance(level.player.origin, level.kamp_kapi) > 1900)
		wait 0.5;

	// --- KAMP GIRISI: 10 + 2 MG42; takviye gelene kadar yeniden dogus
	level.asama = "CAMP_ASSAULT";
	objective_state(3, "done");
	objective_add(4, "active", &"BURYA_OBJ_GIRIS", level.kamp_kapi);
	objective_current(4);
	level thread autoSaveByName("kamp_girisi");
	level thread muzik("burya_muzik_kamp");
	kamp_dis_dogur();
	level thread yedek_dogus();
	level thread leonov_der("kamp");
	ekip_hucum(level.kamp_kapi + (0, -500, 0), 800);
	wait 6;
	level thread leonov_der("mg");
	while (!flag("takviye_indi") && !kamp_icinde(level.player.origin))
		wait 0.5;
	level thread leonov_der("savun");
	// Sovyetler kampa bastirir; biri girince dis dogus durur
	sovyet_emir("kamp");
	ekip_hucum(level.kamp_kapi + (0, 400, 0), 700);
	flag_wait("sovyet_kampta");
	level.ekip_mod = "bekle";
	tum = tum_sovyetler();
	for (i = 0; i < tum.size; i++)
		tum[i] thread alani_temizle();
	objective_state(4, "done");
	level thread autoSaveByName("giris_alindi");

	// --- KAMPI ELE GECIR: ic 15 (binalar dahil) + merkez 7 + bina ici yedek
	level.asama = "CAPTURE_CAMP";
	objective_add(5, "active", &"BURYA_OBJ_ELE", level.kamp_orta);
	objective_current(5);
	level thread leonov_der("temizle");
	level.ic_ai = [];
	level thread gizli_grup("kamp_ic");
	level thread gizli_grup("kamp_merkez");
	level thread bina_ici_dogus(8);
	ekip_hucum(level.kamp_orta, 1300);
	wait 3;
	while (!flag("ic_dogdu") || canli_say(level.ic_ai) > 0 || canli_say(level.kapi_ai) > 0)
		wait 1;
	flag_set("kamp_temiz");
	objective_state(5, "done");
	level thread autoSaveByName("kamp_temiz");

	// --- KARSI SALDIRI: 50 Alman, her yonden
	level.asama = "COUNTER_ATTACK";
	level.ekip_mod = "bekle";
	objective_add(6, "active", &"BURYA_OBJ_SAVUN", level.kamp_orta);
	objective_current(6);
	level thread muzik("burya_muzik_savunma");
	leonov_der("saldiri");
	sovyet_emir("savun");
	level thread kule_nobetcileri();
	level thread bina_mg_nobetcisi();
	while (!kamp_icinde(level.player.origin))
		wait 0.5;
	wait randomfloatrange(22, 27);              // kullanici: kamptaysak 25-30 sn sonra
	karsi_duman();
	wait 3;
	level thread karsi_saldiri(50);
	wait 6;
	level thread leonov_der("geliyorlar");
	flag_wait("karsi_bitti");
	objective_state(6, "done");
	leonov_der("geri");
	level thread autoSaveByName("karsi_saldiri");

	// --- BOMBA (3 patlayici); kurulunca dogrudan 20 sn
	level.asama = "PLANT_EXPLOSIVE";
	level thread muzik("burya_muzik_yolculuk");
	leonov_der("kamp_bizde");
	bombalar = getentarray("bomba", "targetname");
	b = bombalar[0];
	for (i = 0; i < bombalar.size; i++)
		if (bombalar[i].script_noteworthy == "1")
			b = bombalar[i];
	objective_add(7, "active", &"BURYA_OBJ_BOMBA", b.origin);
	for (i = 0; i < bombalar.size; i++)
		objective_additionalposition(7, i, bombalar[i].origin);
	objective_current(7);
	leonov_der("bomba");
	level.kurulan = 0;
	for (i = 0; i < bombalar.size; i++)
		bombalar[i] thread bomba_kur(i);
	while (level.kurulan < bombalar.size)
		wait 0.2;
	flag_set("bomba_kuruldu");
	objective_state(7, "done");

	// --- KACIS: Sovyetler kampi terk eder, disarida comelip izler
	level.asama = "ESCAPE";
	level thread kacis();
	level thread son_almanlar();
	level thread kacis_replikleri();
	sayac = maps\_utility::getstopwatch(60, 20);
	for (i = 0; i < bombalar.size; i++)
		bombalar[i] playloopsound("bomb_tick");
	wait 15;
	level thread muzik_bir("burya_muzik_bomba");  // kullanici: sayacin 15. saniyesinde
	wait 5;
	sayac destroy();
	for (i = 0; i < bombalar.size; i++)
		bombalar[i] stoploopsound();

	// --- UC AYRI PATLAMA
	level.asama = "FINAL_EXPLOSION";
	kamp_patlat(bombalar);
	level thread muzik_bir("burya_muzik_final");
	wait 5;
	oksuruk();

	// --- GOREV SONU
	level.asama = "MISSION_COMPLETE";
	objective_add(8, "active", &"BURYA_OBJ_LEONOV", level.guvenli);
	objective_current(8);
	final_toplan(level.guvenli);
	for (t = 0; t < 80; t++)
	{
		if (distance(level.player.origin, level.leonov.origin) < 230 && (toplandi() || t > 40))
			break;
		wait 0.5;
	}
	objective_state(8, "done");
	leonov_der("final1");
	leonov_der("final2");
	wait 3;
	if (!flag("bitti"))
	{
		flag_set("bitti");
		bolum_sonu();
	}
}

// --------------------------------------------------------------------------
// KONVOY
// --------------------------------------------------------------------------
konvoy()
{
	level.k = [];
	for (g = 1; g <= 3; g++)
	{
		arac_yolcu_hazirla(g, "konvoy" + g, 30);
		a = maps\_vehicle::scripted_spawn(g);
		level.k[g] = a[0];
	}
	level.k[1] thread arac_olumsuz();
	level.k[2] thread arac_olumsuz();
	level.ekip = [];
	for (g = 1; g <= 2; g++)
	{
		if (!isdefined(level.k[g].riders))
			continue;
		for (i = 0; i < level.k[g].riders.size; i++)
		{
			r = level.k[g].riders[i];
			if (!isalive(r))
				continue;
			if (isdefined(r.script_noteworthy) && r.script_noteworthy == "leonov")
				level.leonov = r;
			if (g == 1)
			{
				r.health = 300;                 // kullanici: butun Sovyetler 300
				sovyet_ekle(r);
				continue;
			}
			r.ekip_uyesi = true;
			if (!isdefined(r.script_noteworthy) || r.script_noteworthy != "leonov")
				r.health = 300;
			level.ekip[level.ekip.size] = r;
		}
	}
	if (isdefined(level.leonov))
	{
		level.leonov.animname = "leonov";
		level.leonov thread magic_bullet_shield();     // olumsuz
		level.leonov.dontavoidplayer = true;
	}
	test_yaz("konvoy yolcu: k2=" + yolcu_say(level.k[2]) + " k3=" + yolcu_say(level.k[3]) + " k1=" + yolcu_say(level.k[1]) + " leonov=" + isdefined(level.leonov));
	level.k[3] thread arkadakiler_bakar();
	if (isdefined(level.k[3].riders))                // patlayacak kamyon: can 1
		for (i = 0; i < level.k[3].riders.size; i++)
			if (isalive(level.k[3].riders[i]))
				level.k[3].riders[i].health = 1;
	// oyuncu 2. kamyonun kasasinda (stok beltot.gsc:1613)
	k2 = level.k[2];
	level.player setorigin(k2 gettagorigin("tag_player"));
	level.player setplayerangles(k2.angles);
	level.player playerLinkToDelta(k2, "tag_player", 0.1);
	level.player allowProne(false);
	level.player allowLeanLeft(false);
	level.player allowLeanRight(false);
	flag_wait("kalk");
	level.konvoy_bas = gettime();
	for (g = 1; g <= 3; g++)
		level thread maps\_vehicle::gopath(level.k[g]);
	level thread muzik("burya_muzik_yolculuk");
	level.k[3] thread on_kamyon_patla();       // kullanici: arkadaki kamyon kopru ustunde patlar
	flag_wait("tanitim_bitti");
	wait 2;
	leonov_der("giris");
	k2 waittill("reached_end_node");
	wait 1.2;
	oyuncu_in(k2);
	flag_set("indik");
}

// kullanici: arkadaki kamyonun askerleri yolculuk boyunca bizim kamyona bakar
arkadakiler_bakar()
{
	if (!isdefined(self.riders))
		return;
	while (!flag("konvoy_vuruldu"))
	{
		for (i = 0; i < self.riders.size; i++)
			if (isalive(self.riders[i]))
				self.riders[i] lookat(level.player, 1.2);
		wait 1;
	}
}

yolcu_say(k)
{
	if (!isdefined(k) || !isdefined(k.riders))
		return 0;
	return canli_say(k.riders);
}

on_kamyon_patla()
{
	self waittill("reached_end_node");
	org = self.origin;
	test_yaz("PATLAMA: konvoydan " + ((gettime() - level.konvoy_bas) / 1000.0) + " sn sonra");
	playfx(level._effect["mayin"], org);
	self playsound("explo_mine");
	earthquake(0.5, 2, org, 2600);
	yolcular = [];
	if (isdefined(self.riders))
		yolcular = self.riders;
	self dodamage(self.health * 2 + 5000, (0, 0, 0));
	self notify("death");
	maps\_fx::loopfx("kamyon_duman", org + (0, 0, 60), 0.7);
	maps\_fx::loopfx("kamyon_ates", org + (0, 0, 40), 0.6);
	engel = getent("kopru_engel", "targetname");    // geri donus kapanir
	if (isdefined(engel))
		engel moveZ(0 - 2000, 0.05);
	flag_set("konvoy_vuruldu");
	level thread grup_dogur("pusu");
	level thread asker_der("vuruldu");
	// kullanici: patlayan kamyonun yolculari OLUR (olculdu: kasadakiler hayatta kaliyordu)
	for (t = 0; t < 6; t++)
	{
		for (i = 0; i < yolcular.size; i++)
			oldur(yolcular[i], org);
		ai = getaiarray("allies");
		for (i = 0; i < ai.size; i++)
			if (!isdefined(ai[i].ekip_uyesi) && distance(ai[i].origin, org) < 420)
				oldur(ai[i], org);
		wait 0.5;
	}
}

oldur(g, kaynak)
{
	if (!isalive(g))
		return;
	if (isdefined(level.leonov) && g == level.leonov)
		return;
	g.allowdeath = true;
	g.magic_bullet_shield = undefined;
	g notify("stop magic bullet shield");
	g dodamage(g.health + 5000, kaynak);
}

// stok decoytown.gsc:702-735 kalibi: oyuncu kasadan yere indirilir
oyuncu_in(k)
{
	sag = anglestoright(k.angles);
	hedef = zemin_bul(k.origin + vectorScale(sag, 150));
	org = spawn("script_origin", level.player.origin);
	level.player unlink();
	level.player playerlinktoabsolute(org);
	org moveto(hedef + (0, 0, 4), 0.9, 0.2, 0.3);
	wait 1;
	level.player unlink();
	org delete();
	level.player allowProne(true);
	level.player allowLeanLeft(true);
	level.player allowLeanRight(true);
	level thread sinir_bekcisi();
	g = getent("sinir_kapi_konvoy", "targetname");   // yol gecitlerinde gercek duvar
	if (isdefined(g))
		g moveZ(0 - 4000, 0.05);
	for (i = 0; i < level.ekip.size; i++)
		if (isalive(level.ekip[i]))
			level.ekip[i].ignoreall = false;
	// ondeki kamyondan inenler pusuya hucum eder (dusuk can, olebilirler)
	for (i = 0; i < level.sovyetler.size; i++)
		if (isalive(level.sovyetler[i]))
			level.sovyetler[i] thread sovyet_beyni();
}

// Arac yolculari: stok spawn_group doSpawn() kullanir, oyuncu gorurse ya da yer
// doluysa SESSIZCE dogmaz (metel olcusu). Yolcular stalingradspawn ile dogar.
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
	for (;;)
	{
		self.health = 100000;
		self waittill("damage");
	}
}

// --------------------------------------------------------------------------
// TAKVIYE: TEK Sovyet kamyonu (sofor + 6), inisten 60 sn sonra
// --------------------------------------------------------------------------
takviye_zamanla()
{
	for (t = 0; t < 600; t++)                   // 60 sn; oyuncu kampa girerse hemen (kullanici)
	{
		if (kamp_icinde(level.player.origin))
			break;
		wait 0.1;
	}
	takviye();
}

takviye()
{
	iprintlnbold(&"BURYA_MSG_TAKVIYE");
	level thread asker_der("takviye");
	arac_yolcu_hazirla(4, "takviye1", 24);
	a = maps\_vehicle::scripted_spawn(4);
	k = a[0];
	k thread arac_olumsuz();
	level thread maps\_vehicle::gopath(k);
	yolcu = [];
	if (isdefined(k.riders))
		yolcu = k.riders;
	test_yaz("takviye yolcu=" + canli_say(yolcu));
	k waittill("reached_end_node");
	wait 5;
	for (i = 0; i < yolcu.size; i++)
	{
		if (!isalive(yolcu[i]))
			continue;
		yolcu[i].health = 300;                  // kullanici: butun Sovyetler 300
		sovyet_ekle(yolcu[i]);
		if (flag("sovyet_kampta") && !flag("kamp_temiz"))
			yolcu[i] thread alani_temizle();
		else
			yolcu[i] thread sovyet_beyni();
	}
	flag_set("takviye_indi");
	test_yaz("takviye indi: allies=" + getaiarray("allies").size);
	g = getent("sinir_kapi_takviye", "targetname");
	if (isdefined(g))
		g moveZ(0 - 4000, 0.05);
}

// --------------------------------------------------------------------------
// SOVYET (ekip disi: ondeki kamyon + takviye) -- tek emir: level.sovyet_emir
// --------------------------------------------------------------------------
sovyet_ekle(g)
{
	level.sovyetler[level.sovyetler.size] = g;
}

sovyet_emir(emir)
{
	level.sovyet_emir = emir;
	level notify("sovyet_emir");
	if (emir == "savun" || emir == "kac")
		level.ekip_mod = "bekle";
	tum = tum_sovyetler();
	for (i = 0; i < tum.size; i++)
		tum[i] thread takili_kurtar();
	if (emir == "savun")
	{
		// kullanici: 7 baraka askeri ve kule MG'cileri disinda herkes karakol binasinda,
		// pencerelerin hemen arkasinda (alt kat yurunerek, ust kat gorulmeden yerlestirilir)
		alt = [];
		e = getentarray("ev_siper", "targetname");
		for (i = 0; i < e.size; i++)
			if (e[i].script_noteworthy == "merkez0")
				alt[alt.size] = e[i].origin;
		ust = [];
		e = getentarray("ust_siper", "targetname");
		for (i = 0; i < e.size; i++)
			ust[ust.size] = e[i].origin;
		n = 0;
		for (i = 0; i < tum.size; i++)
		{
			if (isdefined(tum[i].kule_nobetcisi) || isdefined(tum[i].ev_nobeti))
				continue;
			if (n < alt.size)
				tum[i] thread binaya_siper(alt[n], false);
			else if (n - alt.size < ust.size)
				tum[i] thread binaya_siper(ust[n - alt.size], true);
			else
				tum[i] thread binaya_siper(alt[n % alt.size], false);
			n++;
		}
	}
	else if (emir == "kamp")
	{
		for (i = 0; i < level.sovyetler.size; i++)
			if (isalive(level.sovyetler[i]))
				level.sovyetler[i] thread sovyet_beyni();
	}
}

// binadaki siper yerine git; takilirsa ya da ust kattaysa gorulmeden yerine alinir
binaya_siper(yer, ust_kat)
{
	self endon("death");
	self notify("yeni_emir");
	self endon("yeni_emir");
	self allowedstances("stand", "crouch");
	self.goalradius = 12;
	if (ust_kat)
		self setgoalpos(zemin_bul((2700, 2300, 60)));   // once binanin icine
	else
		self setgoalpos(yer);
	son = self.origin;
	bekle = 0;
	for (t = 0; t < 120; t++)
	{
		wait 0.5;
		if (distance(self.origin, yer) < 40)
			break;
		if (distance(self.origin, son) < 24)
			bekle++;
		else
			bekle = 0;
		son = self.origin;
		hazir = (bekle >= 12) || (ust_kat && bina_ici(self.origin));
		if (hazir && !gorunur(self.origin) && !gorunur(yer))
		{
			self teleport(yer);
			break;
		}
	}
	self setgoalpos(yer);
}

takili_kurtar()
{
	self endon("death");
	self notify("kurtar_tek");
	self endon("kurtar_tek");
	self unlink();
	son = self.origin;
	for (t = 0; t < 200; t++)
	{
		wait 3;
		if (level.asama != "FIRST_ENCOUNTER" && level.asama != "ADVANCE_TO_CAMP" && level.asama != "CAMP_ASSAULT")
			return;
		if (distance(self.origin, son) > 40 || distance(self.origin, level.player.origin) < 700)
		{
			son = self.origin;
			self.takili = 0;
			continue;
		}
		if (!isdefined(self.takili))
			self.takili = 0;
		self.takili++;
		if (self.takili >= 3)
		{
			ileri = anglestoforward(level.player getplayerangles());
			p = zemin_bul(level.player.origin - vectorScale((ileri[0], ileri[1], 0), 300) + (randomfloatrange(-120, 120), randomfloatrange(-120, 120), 0));
			if (!gorunur(self.origin) && !gorunur(p))
			{
				self teleport(p);
				self.takili = 0;
				test_yaz("takili asker kurtarildi");
			}
		}
		son = self.origin;
	}
}

// kamp alanini bastan sona tarar: en yakin canli Almanin yanina gider (kamp icinde)
alani_temizle()
{
	self notify("yeni_emir");
	self endon("yeni_emir");
	self endon("death");
	self.pathenemyfightdist = 400;
	self.pathenemylookahead = 400;
	while (!flag("kamp_temiz"))
	{
		hedef = undefined;
		ed = 999999;
		ai = getaiarray("axis");
		for (i = 0; i < ai.size; i++)
		{
			if (!kamp_icinde(ai[i].origin) || isdefined(ai[i].mg_alman))
				continue;
			d = distance(self.origin, ai[i].origin);
			if (d < ed)
			{
				hedef = ai[i];
				ed = d;
			}
		}
		self.goalradius = 180;
		if (isdefined(hedef))
			self setgoalpos(zemin_bul(hedef.origin));
		else
			self setgoalpos(zemin_bul(level.kamp_orta + (randomfloatrange(-900, 900), randomfloatrange(-500, 600), 0)));
		wait randomfloatrange(3, 5);
	}
}

tum_sovyetler()
{
	t = [];
	if (isdefined(level.ekip))
		for (i = 0; i < level.ekip.size; i++)
			if (isalive(level.ekip[i]))
				t[t.size] = level.ekip[i];
	for (i = 0; i < level.sovyetler.size; i++)
		if (isalive(level.sovyetler[i]))
			t[t.size] = level.sovyetler[i];
	return t;
}

sovyet_beyni()
{
	self notify("yeni_emir");
	self endon("yeni_emir");
	self endon("death");
	self.pathenemyfightdist = 600;
	self.pathenemylookahead = 600;
	if (!isdefined(level.sovyet_emir) || level.sovyet_emir == "pusu")
	{
		self bolge_dolas(level.patlama_yeri + (250, 300, 0), 900, -9999, 9999);
		return;
	}
	// kamp: hedef kampin icidir (kullanici: Sovyetlerin tek amaci karakolu almak)
	// Olculdu: inisten hemen sonra arac betigi hedefi eziyordu (kamyonun dogdugu
	// yere kosuyorlardi) -> hedef 3 sn'de bir yeniden verilir
	self.goalradius = 300;
	for (t = 0; t < 20; t++)
	{
		self setgoalpos(zemin_bul(level.kamp_kapi + (0, 150, 0)));
		if (distance(self.origin, level.kamp_kapi) < 450)
			break;
		wait 3;
	}
	self bolge_dolas(level.kamp_orta, 1300, -9999, 9999);
}

kamp_siperleri()
{
	yer = [];
	for (i = 0; i < level.siper.size; i++)
	{
		p = level.siper[i].origin;
		if (kamp_icinde(p) && !bina_ici(p))
			yer[yer.size] = level.siper[i];
	}
	return yer;
}

kamp_icinde(p)
{
	return (p[0] > 1700 && p[0] < 4200 && p[1] > 1500 && p[1] < 3000);
}

sovyet_kampta_mi()
{
	if (kamp_icinde(level.player.origin))
		return true;
	ai = getaiarray("allies");
	for (i = 0; i < ai.size; i++)
		if (kamp_icinde(ai[i].origin))
			return true;
	return false;
}

// --------------------------------------------------------------------------
// ALMANLAR
// --------------------------------------------------------------------------
// AI butcesi dolu ise bekleyip zorla dogurur (spawner yeniden kullanilabilir)
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

// oyuncunun goremedigi bir noktada dogur (kullanici: "gormedigimiz yerlerde")
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
			if (!isdefined(s))
				continue;
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

grup_dogur(ad)
{
	sp = getentarray(ad, "targetname");
	dogan = [];
	for (i = 0; i < sp.size; i++)
	{
		g = dogur(sp[i]);
		sp[i] delete();
		if (!isdefined(g))
			continue;
		dogan[dogan.size] = g;
		if (ad == "pusu")
			g thread bolge_dolas(level.patlama_yeri + (250, 300, 0), 850, -9999, 9999);
		else if (ad == "kamp_dis")
			g thread bolge_dolas(level.kamp_kapi + (0, 200, 0), 700, -9999, 9999);
		wait 0.1;
	}
	return dogan;
}

// kamp ici gruplar: her spawner gorulmedigi anda (en fazla 10 sn beklenir)
gizli_grup(ad)
{
	sp = getentarray(ad, "targetname");
	for (i = 0; i < sp.size; i++)
	{
		for (t = 0; t < 20 && gorunur(sp[i].origin); t++)
			wait 0.5;
		g = dogur(sp[i]);
		sp[i] delete();
		if (!isdefined(g))
			continue;
		level.ic_ai[level.ic_ai.size] = g;
		if (ad == "kamp_merkez")
			g thread bolge_dolas((3000, 2300, 0), 480, -9999, 9999);
		else if (bina_ici(g.origin) || isdefined(g.script_noteworthy))
			g thread bolge_dolas(g.origin, 260, -9999, 9999);
		else
			g thread bolge_dolas(level.kamp_orta, 1150, -9999, 9999);
		wait 0.2;
	}
	if (!isdefined(level.ic_grup_bitti))
		level.ic_grup_bitti = 0;
	level.ic_grup_bitti++;
	if (level.ic_grup_bitti >= 2)
		flag_set("ic_dogdu");
}

// kamp dis savunmasi + kule MG42 nisancilari (stok _spawner use_a_turret)
kamp_dis_dogur()
{
	mg = getentarray("kule_mg", "targetname");
	sp = getentarray("kamp_mg", "targetname");
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
		g.health = 100;
		g.anim_disableLongDeath = true;
		g.mg_alman = true;
		g allowedstances("prone");
		g thread mg_kalk(en);
	}
	level.kapi_ai = grup_dogur("kamp_dis");
}

// yatarak doger, oyuncu yaklasinca kalkar; MG'yi BIRAKMAZ (kullanici)
mg_kalk(mg)
{
	self endon("death");
	for (t = 0; t < 400; t++)
	{
		if (distance(level.player.origin, self.origin) < 1700)
			break;
		wait 0.1;
	}
	wait randomfloatrange(0.5, 1.5);
	self allowedstances("stand", "crouch");
	self.goalradius = 4;
	self setgoalpos(self.origin);
	wait 0.8;
	mg setmode("auto_ai");
	for (;;)
	{
		sahip = mg getturretowner();
		if (!isdefined(sahip) || sahip != self)
		{
			self setgoalpos(self.origin);
			self useturret(mg);                 // stok _spawner use_a_turret
		}
		wait 1;
	}
}

// takviye gelene kadar: kapi savunmasi 10'un altina dustukce 2-5 sn sonra yenisi
yedek_dogus()
{
	level endon("yedek_dur");
	level thread yedek_durdur();
	sp = getentarray("kamp_yedek", "targetname");
	for (;;)
	{
		while (canli_say(level.kapi_ai) >= 10)
			wait 0.5;
		wait randomfloatrange(2, 5);
		g = gizli_dogur(sp, 700);
		if (!isdefined(g))
			continue;
		level.kapi_ai[level.kapi_ai.size] = g;
		g thread bolge_dolas(level.kamp_kapi + (0, 250, 0), 650, -9999, 9999);
	}
}

yedek_durdur()
{
	// takviye inince ya da oyuncu takviyeden once kampa girerse
	while (!flag("takviye_indi") && !kamp_icinde(level.player.origin))
		wait 0.5;
	bas = gettime();
	while (!sovyet_kampta_mi() && gettime() - bas < 120000)
		wait 0.5;
	level notify("yedek_dur");
	flag_set("sovyet_kampta");
	test_yaz("sovyet kampta: dis dogus durdu");
}

// Sovyet kampa girdikten sonra: yalniz binalarin icinde (ve bomba odalarinda) dogus
bina_ici_dogus(adet)
{
	sp = getentarray("bina_yedek", "targetname");
	for (n = 0; n < adet; n++)
	{
		while (canli_say(level.ic_ai) >= 14)
			wait 0.5;
		wait randomfloatrange(2, 5);
		g = gizli_dogur(sp, 500);
		if (!isdefined(g))
			continue;
		level.ic_ai[level.ic_ai.size] = g;
		g thread bolge_dolas(g.origin, 300, -9999, 9999);
	}
}

// KARSI SALDIRI: 5-6 sn'de 5-6 Alman, ormanin her yonunden
karsi_saldiri(toplam)
{
	sp = getentarray("karsi", "targetname");
	level.karsi_ai = [];
	dogan = 0;
	while (dogan < toplam)
	{
		n = 5 + randomint(2);
		for (k = 0; k < n && dogan < toplam; k++)
		{
			while (canli_say(getaiarray("axis")) >= 16)
				wait 0.5;
			g = gizli_dogur(sp, 900);
			if (!isdefined(g))
				continue;
			dogan++;
			if (dogan == 5)
				level thread ev_sovyetleri();       // kullanici: bir kez, bomba evinde 7 Sovyet
			level.karsi_ai[level.karsi_ai.size] = g;
			g thread karsi_alman();
			wait 0.3;
		}
		test_yaz("karsi saldiri: dogan=" + dogan + " canli=" + canli_say(level.karsi_ai));
		wait randomfloatrange(5, 6);
	}
	while (canli_say(level.karsi_ai) > 0)
		wait 1;
	flag_set("karsi_bitti");
	test_yaz("karsi saldiri bitti: 50");
}

// saldiridan once dogus noktalarinda duman
karsi_duman()
{
	sp = getentarray("karsi", "targetname");
	for (i = 0; i < sp.size; i++)
	{
		playfx(level._effect["duman_bombasi"], zemin_bul(sp[i].origin + (randomfloatrange(-80, 80), randomfloatrange(-80, 80), 0)));
		wait randomfloatrange(0.1, 0.4);
	}
}

// baraka A'da (bomba evi) 7 Sovyet: biri kapida, digerleri pencerelerde
ev_sovyetleri()
{
	sp = getentarray("ev_sovyet", "targetname");
	for (i = 0; i < sp.size; i++)
	{
		sp[i].count = 1;
		g = sp[i] stalingradspawn();
		if (spawn_failed(g))
			continue;
		g.health = 300;
		g.goalradius = 16;
		g setgoalpos(sp[i].origin);
		g allowedstances("stand", "crouch");
		sovyet_ekle(g);
		g.ev_nobeti = true;
		wait 0.1;
	}
	test_yaz("ev sovyetleri: " + sp.size);
}

// kosu sirasinda mermi yerse 4 sn durup carpisir, sonra yine kosar
vurulunca_dur()
{
	self endon("death");
	self endon("kampa_girdi");
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

karsi_alman()
{
	self endon("death");
	// kullanici: kamp alanina girene kadar durmadan kosarlar (yolda ates ederler)
	self.pathenemyfightdist = 0;
	self.pathenemylookahead = 0;
	self.ignoresuppression = true;
	self.goalradius = 96;
	// olculdu: kamp icinde rastgele nokta kapali binaya dusuyordu (yol yok -> yerinde
	// duruyorlardi). Hedef: kapinin ici (tek giris), oradan binadaki Sovyetler
	giris = zemin_bul(level.kamp_kapi + (randomfloatrange(-150, 150), 330, 0));
	self thread vurulunca_dur();
	for (t = 0; t < 120 && !kamp_icinde(self.origin); t++)
	{
		self setgoalpos(giris);
		wait 0.5;
	}
	self notify("kampa_girdi");
	self.pathenemyfightdist = 350;
	self.pathenemylookahead = 350;
	// kullanici: Almanlar Sovyetlerin oldugu yere gidip onlari oldurup kampi almaya calisir
	for (;;)
	{
		hedef = level.player;
		ed = distance(self.origin, level.player.origin);
		tum = tum_sovyetler();
		for (i = 0; i < tum.size; i++)
		{
			if (isdefined(tum[i].kule_ustunde) || isdefined(tum[i].bina_mg) || tum[i].origin[2] > 150)
				continue;                       // yuksekteki (kule, ust kat) Sovyetlere yurunemez
			d = distance(self.origin, tum[i].origin);
			if (d < ed)
			{
				hedef = tum[i];
				ed = d;
			}
		}
		self.goalradius = 160;
		self setgoalpos(zemin_bul(hedef.origin));
		wait randomfloatrange(4, 6);
	}
}

// merkez bina ust kat penceresindeki MG42: rastgele bir Sovyet kullanir (ust katta
// yol agi yok -> gorulmedigi anda MG'nin arkasina alinir)
bina_mg_nobetcisi()
{
	mg = getent("bina_mg", "targetname");
	yer = getent("bina_mg_yer", "targetname").origin;
	aday = [];
	tum = tum_sovyetler();
	for (i = 0; i < tum.size; i++)
		if (!isdefined(tum[i].kule_nobetcisi) && (!isdefined(level.leonov) || tum[i] != level.leonov))
			aday[aday.size] = tum[i];
	if (!aday.size)
		return;
	g = aday[randomint(aday.size)];
	g endon("death");
	g notify("yeni_emir");
	g endon("yeni_emir");
	g.kule_nobetcisi = true;
	g.bina_mg = true;
	for (t = 0; t < 40 && (gorunur(g.origin) || gorunur(yer)); t++)
		wait 0.5;
	yer = mg.origin - vectorScale(anglestoforward(mg.angles), 34);
	yer = (yer[0], yer[1], getent("bina_mg_yer", "targetname").origin[2]);
	g teleport(yer);
	g.goalradius = 8;
	g setgoalpos(yer);
	g.kule_ustunde = mg;
	g.ignoreall = false;
	g allowedstances("stand", "crouch");
	mg setmode("auto_ai");
	test_yaz("bina MG nobetcisi yerinde");
	for (;;)
	{
		sahip = mg getturretowner();
		if (!isdefined(sahip) || sahip != g)
			g useturret(mg);
		wait 1;
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

// SIPER DEGISTIREN SAVUNUCU (krasnoye/metel kalibi)
bolge_dolas(merkez, yaricap, zmin, zmax)
{
	self endon("death");
	self endon("yeni_emir");
	wait randomfloatrange(1, 4);
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
			if (bina_ici(n.origin) != bina_ici(self.origin))
				continue;                       // olculdu: bina kapilarindan iceri yol bagi tek yonlu
			if (distance((n.origin[0], n.origin[1], 0), (merkez[0], merkez[1], 0)) > yaricap)
				continue;
			dn = distance(n.origin, self.origin);
			if (dn < 100 || dn > 750)
				continue;
			if (self.team == "axis" && distance(n.origin, p) < 300)
				continue;
			if (self.team == "axis" && yakin && distance(n.origin, p) < distance(self.origin, p))
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
			wait randomfloatrange(7, 14);
	}
}

// --------------------------------------------------------------------------
// KULE NOBETCILERI: karsi saldirida iki Sovyet el merdiveninden cikip MG'ye
// gecer (yol agi: ladder_up negotiation); takilirsa gorulmeden platforma alinir
// --------------------------------------------------------------------------
kule_nobetcileri()
{
	mg = getentarray("kule_mg", "targetname");
	aday = tum_sovyetler();
	n = 0;
	for (i = 0; i < aday.size && n < mg.size; i++)
	{
		g = aday[i];
		if (isdefined(level.leonov) && g == level.leonov)
			continue;
		g.kule_nobetcisi = true;
		g thread kuleye_cik(mg[n]);
		n++;
	}
}

kuleye_cik(mg)
{
	self endon("death");
	self notify("yeni_emir");
	self endon("yeni_emir");
	ust = undefined;
	e = getentarray("kule_ust", "targetname");
	for (i = 0; i < e.size; i++)
		if (e[i].script_noteworthy == mg.script_noteworthy)
			ust = e[i].origin;
	self.goalradius = 24;
	self setgoalpos(ust);
	bas = gettime();
	while (distance(self.origin, ust) > 60)
	{
		if (gettime() - bas > 25000 && !gorunur(self.origin) && !gorunur(ust))
			self teleport(ust);
		wait 0.5;
	}
	self.kule_ustunde = mg;
	self allowedstances("stand", "crouch");
	mg setmode("auto_ai");
	for (;;)
	{
		sahip = mg getturretowner();
		if (!isdefined(sahip) || sahip != self)
			self useturret(mg);
		wait 1;
	}
}

// --------------------------------------------------------------------------
// EKIP BEYNI (metel): takip / hucum / bekle -- yalniz konvoy ekibi
// --------------------------------------------------------------------------
ekip_beyni()
{
	for (;;)
	{
		wait 1;
		ai = [];
		if (isdefined(level.ekip))
			for (i = 0; i < level.ekip.size; i++)
				if (isalive(level.ekip[i]) && !isdefined(level.ekip[i].kule_nobetcisi))
					ai[ai.size] = level.ekip[i];
		if (!flag("indik"))
			continue;
		if (level.ekip_mod == "takip")
			ekip_takip_et(ai);
		else if (level.ekip_mod == "hucum")
			ekip_hucum_et(ai);
	}
}

ekip_hucum(merkez, yaricap)
{
	level.hucum_siper = [];
	for (i = 0; i < level.siper.size; i++)
		if (distance((level.siper[i].origin[0], level.siper[i].origin[1], 0), (merkez[0], merkez[1], 0)) < yaricap)
			if (!bina_ici(level.siper[i].origin))
				level.hucum_siper[level.hucum_siper.size] = level.siper[i];
	if (level.hucum_siper.size)
		level.ekip_mod = "hucum";
	else
		level.ekip_mod = "takip";
}

ekip_takip_et(ai)
{
	p = level.player.origin;
	ileri = anglestoforward(level.player getplayerangles());
	yaw = vectortoangles((ileri[0], ileri[1], 0))[1];
	for (i = 0; i < ai.size; i++)
	{
		g = ai[i];
		a = yaw + 180 + (i - (ai.size - 1) / 2.0) * 24;
		r = 200 + (i % 3) * 65;
		hedef = zemin_bul(p + (cos(a) * r, sin(a) * r, 0));
		g.pathenemyfightdist = 500;
		if (!isdefined(g.takip_hedef) || distance(g.takip_hedef, hedef) > 160 || distance(g.origin, p) > 900)
		{
			g.takip_hedef = hedef;
			g.goalradius = 96;
			g setgoalpos(hedef);
		}
	}
}

// HUCUM: 350'lik siciramalarla siperden sipere, yolda catisarak
ekip_hucum_et(ai)
{
	for (i = 0; i < ai.size; i++)
	{
		g = ai[i];
		g.pathenemyfightdist = 600;
		g.pathenemylookahead = 600;
		n = level.hucum_siper[i % level.hucum_siper.size];
		if (isdefined(g.hucum_zaman) && gettime() < g.hucum_zaman)
			continue;
		g.hucum_zaman = gettime() + randomintrange(5000, 8000);
		d = distance(g.origin, n.origin);
		hedef = n.origin;
		if (d > 400)
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

// merkez bina ici (yol agi: icten disa bag var, distan ice yok -- kr_deney olcusu)
bina_ici(p)
{
	return (p[0] > 2500 && p[0] < 3500 && p[1] > 1980 && p[1] < 2620);
}

zemin_bul(nokta)
{
	tr = bulletTrace(nokta + (0, 0, 400), nokta - (0, 0, 800), false, undefined);
	return tr["position"] + (0, 0, 4);
}

// --------------------------------------------------------------------------
// BOMBA (stok demolition.gsc:1666-1724) VE YIKIM (demolition buildingExplodes)
// --------------------------------------------------------------------------
bomba_kur(no)
{
	t = getent(self.target, "targetname");
	self show();
	t.origin = t.eski_yer;
	t sethintstring(&"BURYA_PLATFORM_BOMBA_KUR");
	t waittill("trigger");
	t delete();
	self setmodel("xmodel/military_tntbomb");
	self playsound("explo_plant_no_tick");
	objective_additionalposition(7, no, (0, 0, 0));
	level.kurulan++;
	test_yaz("patlayici kuruldu: " + level.kurulan);
}

// kullanici: bomba kurulunca butun Sovyetler kampi terk eder, disarida comelip izler
kacis()
{
	sovyet_emir("kac");
	tum = tum_sovyetler();
	yer = [];
	for (i = 0; i < level.siper.size; i++)
		if (distance(level.siper[i].origin, level.guvenli) < 320)
			yer[yer.size] = level.siper[i];
	for (i = 0; i < tum.size; i++)
		if (!isdefined(tum[i].bina_mg))           // kullanici: ust kat MG'cisi patlamaya kadar kalir
			tum[i] thread kacan_asker(i, yer);
}

// kullanici: oyuncu kamp alanindan cikinca evlerin icinde Almanlar doger, pencerelere
// siper alip bize ates eder, sonra kamp icinde panikle kacisir; patlama onlari yakalar
son_almanlar()
{
	while (kamp_icinde(level.player.origin) && !flag("patladi"))
		wait 0.2;
	if (flag("patladi"))
		return;
	sp = getentarray("bina_yedek", "targetname");
	pen = getentarray("ev_siper", "targetname");
	ai = [];
	for (i = 0; i < sp.size; i++)
	{
		sp[i].count = 1;
		g = sp[i] stalingradspawn();
		if (spawn_failed(g))
			continue;
		ai[ai.size] = g;
		en = undefined;
		for (k = 0; k < pen.size; k++)
			if (!isdefined(pen[k].dolu) && (!isdefined(en) || distance(pen[k].origin, g.origin) < distance(en.origin, g.origin)))
				en = pen[k];
		g.goalradius = 16;
		if (isdefined(en))
		{
			en.dolu = true;
			g setgoalpos(en.origin);
		}
		g.favoriteenemy = level.player;
	}
	test_yaz("son almanlar: " + ai.size);
	wait randomfloatrange(5, 6);
	for (i = 0; i < ai.size; i++)
		if (isalive(ai[i]))
			ai[i] thread panik();
}

panik()
{
	self endon("death");
	self.ignoreall = true;
	self.goalradius = 64;
	for (;;)
	{
		self setgoalpos(zemin_bul(level.kamp_orta + (randomfloatrange(-900, 900), randomfloatrange(-500, 600), 0)));
		wait randomfloatrange(1.5, 3);
	}
}

kacan_asker(i, yer)
{
	self endon("death");
	self notify("yeni_emir");
	self endon("yeni_emir");
	self.ignoreall = true;
	if (isdefined(self.kule_ustunde))
	{
		self stopuseturret();
		self.kule_ustunde = undefined;
	}
	self allowedstances("stand", "crouch", "prone");
	if (i < yer.size)
	{
		self.goalradius = 32;
		self setgoalnode(yer[i]);
	}
	else
	{
		a = 200 + (i - yer.size) * 14;
		r = 260 + (i % 3) * 70;
		self.goalradius = 48;
		self setgoalpos(zemin_bul(level.guvenli + (cos(a) * r, sin(a) * r, 0)));
	}
	bas = gettime();
	self hedef_bekle(25);
	// kulede kalan (merdiven indirmediyse): gorulmeden kule dibine
	if (self.origin[2] > 150 && !gorunur(self.origin))
		self teleport(zemin_bul(self.origin + (0, -200, 0)));
	self waittill_goal_ya_da(20);
	self allowedstances("crouch");
	self.ignoreall = false;
}

waittill_goal_ya_da(sure)
{
	self endon("goal");
	wait sure;
}

kacis_replikleri()
{
	asker_der("kac1");
	wait 2;
	asker_der("kac2");
	wait 1.5;
	asker_der("kac3");
	wait 1.5;
	asker_der("kac4");
}

// UC AYRI PATLAMA: baraka -> depo -> merkez bina; kuleler devrilir; kamptaki
// her canli olur; giris enkazla kapanir
kamp_patlat(bombalar)
{
	flag_set("patladi");
	test_yaz("KAMP PATLADI");
	sira = [];
	sira[0] = "3";
	sira[1] = "2";
	sira[2] = "1";
	no = [];
	yer = [];
	for (i = 0; i < bombalar.size; i++)          // olculdu: silinen bombanin alani okunuyordu
	{
		no[i] = bombalar[i].script_noteworthy;
		yer[i] = bombalar[i].origin;
	}
	for (s = 0; s < sira.size; s++)
	{
		for (i = 0; i < no.size; i++)
		{
			if (no[i] != sira[s])
				continue;
			o = yer[i];
			bombalar[i] delete();
			if (sira[s] == "3")
				ev_patlat("baraka_a", o, (2100, 2210, 60));
			else if (sira[s] == "2")
				ev_patlat("depo_a", o, (3375, 2860, 60));
			else
				merkez_patlat(o);
		}
		if (s == 0)
			level thread kule_devril(0);
		if (s == 1)
			level thread kule_devril(1);
		kamptakileri_oldur();
		wait 1.6;
	}
	// kalan evler ve kamp kamyonu (zincirleme)
	ev = [];
	ev[0] = "baraka_b";
	ev[1] = "depo_b";
	ev[2] = "baraka_c";
	ev[3] = "baraka_d";
	mz = [];
	mz[0] = (2030, 2665, 60);
	mz[1] = (2645, 2830, 60);
	mz[2] = (3930, 1950, 60);
	mz[3] = (3930, 2575, 60);
	for (i = 0; i < ev.size; i++)
	{
		level thread ev_patlat(ev[i], mz[i], mz[i]);
		if (i == 1)
			level thread kamyon_patlat();
		wait randomfloatrange(0.5, 0.9);
	}
	kamptakileri_oldur();
	level.kapi_enkaz moveto(level.kapi_enkaz.origin + (9000, 0, 0 - 2000), 0.05);
	wait 0.1;
	level.kapi_enkaz show();
	level.kapi_enkaz solid();
	playfx(level._effect["bina_toz"], level.kamp_kapi + (0, 200, 0));
}

kamyon_patlat()
{
	k = getent("kamp_kamyon", "targetname");
	if (!isdefined(k))
		return;
	o = k.origin;
	playfx(level._effect["mayin"], o);
	playfx(level._effect["bina_buyuk"], o + (0, 0, 40));
	s = spawn("script_origin", o + (0, 0, 60));
	s playsound("explo_mine");
	k setmodel("xmodel/vehicle_opel_blitz_woodland_d_static");
	earthquake(0.3, 1, o, 2500);
	maps\_fx::loopfx("kamyon_ates", o + (0, 0, 40), 0.6);
	maps\_fx::loopfx("kamyon_duman", o + (0, 0, 70), 0.7);
}

kamptakileri_oldur()
{
	ai = getaiarray();
	for (i = 0; i < ai.size; i++)
		if (kamp_icinde(ai[i].origin))
			oldur(ai[i], ai[i].origin);
	if (kamp_icinde(level.player.origin))
	{
		level.player enableHealthShield(false);
		level.player dodamage(level.player.health + 5000, level.player.origin);
	}
}

ev_patlat(ad, bomba_yeri, merkez)
{
	playfx(level._effect["bina_buyuk"], bomba_yeri + (0, 0, 40));
	playfx(level._effect["mayin"], bomba_yeri);
	playfx(level._effect["bina_pencere"], merkez + (0, 0, 60));
	s = spawn("script_origin", merkez + (0, 0, 100));
	s playsound("demolition_demoexplosion");
	earthquake(0.45, 1.6, merkez, 6000);
	radiusDamage(merkez, 600, 1000, 600);
	u = level.yikilir[ad];
	u notsolid();
	u rotateroll(randomfloatrange(-5, 5), 2.6, 2.0, 0);
	u movez(0 - 128, 2.6, 2.2, 0);               // kullanici: cati asagi dogru coker (yok olmaz)
	y = level.yikik[ad];
	y moveto(y.origin + (9000, 0, 0 - 2000), 0.05);
	wait 0.1;
	y show();
	y solid();
	enkaz_sac(merkez, 6);
	maps\_fx::loopfx("bina_ates", merkez + (-120, 0, 20), 0.6);
	maps\_fx::loopfx("bina_ates", merkez + (140, 40, 20), 0.6);
	maps\_fx::loopfx("bina_duman", merkez + (0, 0, 120), 1.5);
}

merkez_patlat(bomba_yeri)
{
	fx = getentarray("bina_fx", "targetname");
	merkez = (3000, 2300, 60);
	ses = spawn("script_origin", merkez + (0, 0, 200));
	ses playsound("demolition_demoexplosion");
	earthquake(0.5, 4, merkez, 7000);
	playfx(level._effect["bina_buyuk"], bomba_yeri + (0, 0, 40));
	for (i = 0; i < fx.size; i++)
	{
		playfx(level._effect["bina_taban"], fx[i].origin);
		wait randomfloatrange(0.05, 0.15);
	}
	playfx(level._effect["bina_buyuk"], merkez + (0, 0, 120));
	playfx(level._effect["bina_pencere"], (3000, 1975, 110));
	playfx(level._effect["bina_pencere"], (2650, 1975, 250));
	playfx(level._effect["bina_pencere"], (3350, 2625, 250));
	playfx(level._effect["bina_toz"], merkez);
	radiusDamage(merkez, 900, 1000, 900);
	esya = getentarray("bina_esya", "targetname");
	for (i = 0; i < esya.size; i++)
		esya[i] delete();
	bmg = getent("bina_mg", "targetname");
	if (isdefined(bmg))
		bmg delete();
	// kullanici: ust kisim yok olmasin, asagi dogru yavasca coksun
	ses playsound("demolition_building_collapse");
	level.bina_saglam notsolid();
	level.bina_saglam rotateroll(4, 3.2, 2.4, 0);
	level.bina_saglam movez(0 - 330, 3.2, 2.6, 0);
	for (k = 0; k < 4; k++)
	{
		playfx(level._effect["bina_toz"], merkez + (randomfloatrange(-400, 400), randomfloatrange(-250, 250), 0));
		enkaz_sac(merkez + (0, 0, 120), 2);
		wait 0.8;
	}
	level.bina_yikik moveto(level.bina_yikik.origin + (9000, 0, 0 - 2000), 0.05);
	wait 0.1;
	level.bina_yikik show();
	level.bina_yikik solid();
	enkaz_sac(merkez, 8);
	level thread merkez_son(merkez);
}

merkez_son(merkez)
{
	wait 0.5;
	playfx(level._effect["bina_sutun"], merkez + (-250, 0, 0));
	playfx(level._effect["bina_sutun"], merkez + (250, 0, 0));
	earthquake(0.3, 6, merkez, 7000);
	wait 2;
	maps\_fx::loopfx("bina_toz_son", merkez, 6);
	maps\_fx::loopfx("bina_ates", merkez + (-300, -120, 30), 0.6);
	maps\_fx::loopfx("bina_ates", merkez + (260, 140, 30), 0.6);
	maps\_fx::loopfx("bina_duman", merkez + (0, 0, 80), 1.5);
}

// tahta parcalari havaya savrulur (stok moveGravity)
enkaz_sac(merkez, adet)
{
	m = [];
	m[0] = "xmodel/gully_bridge_debris_sm01";
	m[1] = "xmodel/gully_bridge_debris_sm02";
	m[2] = "xmodel/gully_bridge_debris_sm03";
	m[3] = "xmodel/moscow_boards_1a";
	m[4] = "xmodel/moscow_boards_2b";
	for (i = 0; i < adet; i++)
	{
		p = spawn("script_model", merkez + (randomfloatrange(-120, 120), randomfloatrange(-120, 120), randomfloatrange(60, 160)));
		p setmodel(m[randomint(m.size)]);
		p.angles = (randomint(360), randomint(360), randomint(360));
		p thread parca_uc();
	}
}

parca_uc()
{
	hiz = (randomfloatrange(-260, 260), randomfloatrange(-260, 260), randomfloatrange(300, 520));
	self movegravity(hiz, 1.6);
	self rotatevelocity((randomfloatrange(-400, 400), randomfloatrange(-400, 400), randomfloatrange(-400, 400)), 1.6);
	wait 1.6;
	tr = bulletTrace(self.origin + (0, 0, 200), self.origin - (0, 0, 2000), false, undefined);
	self.origin = tr["position"] + (0, 0, 2);
}

// kule YAVASCA devrilir, tahta parcalari dokulur; MG ve kalanlar yok olur
kule_devril(no)
{
	kuleler = getentarray("kule", "targetname");
	k = undefined;
	for (i = 0; i < kuleler.size; i++)
		if (kuleler[i].script_noteworthy == "" + (no + 1))
			k = kuleler[i];
	if (!isdefined(k))
		return;
	mg = getentarray("kule_mg", "targetname");
	for (i = 0; i < mg.size; i++)
		if (distance((mg[i].origin[0], mg[i].origin[1], 0), (k.origin[0], k.origin[1], 0)) < 200)
			mg[i] delete();
	o = k.origin;
	playfx(level._effect["kule_tahta"], o + (0, 0, 120));
	playfx(level._effect["kule_kirik"], o + (0, 0, 40));
	s = spawn("script_origin", o + (0, 0, 120));
	s playsound("demolition_building_collapse");
	yon = 1;
	if (no == 1)
		yon = -1;
	// bati kulesi (no 0) DOGUYA devrilir (kullanici), dogu kulesi yana
	if (no == 0)
		k rotatepitch(12, 1.2, 0.6, 0);             // once yavasca yatar
	else
		k rotateroll(yon * 12, 1.2, 0.6, 0);
	enkaz_sac(o + (0, 0, 150), 4);
	wait 1.2;
	if (no == 0)
		k rotatepitch(66, 2.4, 2.2, 0);             // sonra hizlanarak yikilir
	else
		k rotateroll(yon * 66, 2.4, 2.2, 0);
	k movez(-70, 2.4, 2.2, 0);
	wait 2.4;
	playfx(level._effect["kule_toz"], o + (0, yon * 0, 10));
	playfx(level._effect["kule_tahta"], o + (0, 0, 30));
	earthquake(0.25, 1, o, 2000);
	enkaz_sac(o + (0, 0, 40), 5);
}

oksuruk()
{
	asker_der("oksur1");
	wait 2;
	asker_der("oksur2");
	wait 1.4;
	asker_der("oksur3");
}

// ekip guvenli alanda Leonov'un cevresinde toplanir (oyuncuya bir bosluk)
final_toplan(merkez)
{
	level.ekip_mod = "bekle";
	g = level.leonov;
	g notify("yeni_emir");
	g allowedstances("stand", "crouch", "prone");
	g.goalradius = 24;
	g setgoalpos(zemin_bul(merkez));
	digerleri = [];
	for (i = 0; i < level.ekip.size; i++)
		if (isalive(level.ekip[i]) && level.ekip[i] != g)
			digerleri[digerleri.size] = level.ekip[i];
	n = digerleri.size + 1;
	for (i = 0; i < digerleri.size; i++)
	{
		a = 45 + 360.0 * (i + 1) / n;
		p = zemin_bul(merkez + (cos(a) * 160, sin(a) * 160, 0));
		digerleri[i] notify("yeni_emir");
		digerleri[i] allowedstances("stand", "crouch", "prone");
		digerleri[i].goalradius = 20;
		digerleri[i].cember_yer = p;
		digerleri[i] setgoalpos(p);
	}
	level.cember_ekip = digerleri;
}

toplandi()
{
	if (!isdefined(level.cember_ekip))
		return true;
	for (i = 0; i < level.cember_ekip.size; i++)
	{
		g = level.cember_ekip[i];
		if (!isalive(g) || !isdefined(g.cember_yer))
			continue;
		if (distance((g.origin[0], g.origin[1], 0), (g.cember_yer[0], g.cember_yer[1], 0)) > 80)
			return false;
	}
	return true;
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
	perde fadeOverTime(7);
	perde.alpha = 1;
	wait 7.5;
	test_yaz("GOREV TAMAM");
	missionSuccess("credits", false);
}

// --------------------------------------------------------------------------
// SES / MUZIK. Olculdu: ayni aktorde bildirimli ikinci playsound betik hatasi
// veriyordu ("issued a second playsound with notification string") ve replik
// sessiz kaliyordu -> her replik kendi script_origin'inden (aktore bagli) calar.
// --------------------------------------------------------------------------
leonov_der(replik)
{
	if (!isdefined(level.leonov) || !isalive(level.leonov))
		return;
	if (!isdefined(level.replik_no))
		level.replik_no = 0;
	level.replik_no++;
	no = level.replik_no;
	level thread leonov_soyle(replik, no);
	for (t = 0; t < 90; t++)                    // en fazla 9 sn beklenir
	{
		if (isdefined(level.replik_bitti) && level.replik_bitti >= no)
			return;
		wait 0.1;
	}
}

leonov_soyle(replik, no)
{
	g = level.leonov;
	if (isalive(g))
	{
		g setBattleChatter(false);
		ses_cal(g, "burya_leonov_" + replik, 9);
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
	org waittill_any_timeout_burya(sure, "ses_bitti", "yok");
	org delete();
}

waittill_any_timeout_burya(sure, a, b)
{
	self endon(a);
	self endon(b);
	wait sure;
}

// Leonov disinda bir ekip askeri soyler (yoksa oyuncunun yaninda)
asker_der(ad)
{
	konusan = undefined;
	if (isdefined(level.ekip))
		for (i = 0; i < level.ekip.size; i++)
			if (isalive(level.ekip[i]) && (!isdefined(level.leonov) || level.ekip[i] != level.leonov))
			{
				konusan = level.ekip[i];
				break;
			}
	if (!isdefined(konusan))
		konusan = level.player;
	ses_cal(konusan, "burya_asker_" + ad, 6);
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

// --------------------------------------------------------------------------
// OYUNCU SINIRI (metel): cokgen disina cikarsa son gecerli yerine
// --------------------------------------------------------------------------
sinir_bekcisi()
{
	son = level.player.origin;
	disari = 0;
	for (;;)
	{
		p = level.player.origin;
		// sinirda gercek gorunmez duvar var; betik yalniz kacak durumlarda (1 sn
		// boyunca disarida) geri alir -- her karede isinlama ekrani titretiyordu
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

// --------------------------------------------------------------------------
// TEST (kr_test 1): butun akisi oynatir, her adimi "dvar set kr_log" ile yazar
// --------------------------------------------------------------------------
test_yaz(msg)
{
	setcvar("kr_log", msg);
}

otomatik_test()
{
	level thread test_olumsuz();
	level thread test_durum();
	flag_wait("konvoy_vuruldu");
	wait 3;
	test_yaz("pusu dogdu: axis=" + getaiarray("axis").size + " allies=" + getaiarray("allies").size);
	wait 6;
	test_oldur();
	flag_wait("pusu_temiz");
	test_yaz("pusu temiz");
	wait 3;
	level.player setorigin(zemin_bul(level.kamp_kapi + (0, -1500, 0)));
	// takviye gelene kadar kapidakiler olduruldukce yenileri dogmali
	while (!flag("takviye_indi"))
	{
		wait 4;
		if (level.asama == "CAMP_ASSAULT")
			test_oldur();
	}
	wait 3;
	level.player setorigin(zemin_bul(level.kamp_kapi + (0, 300, 0)));   // Sovyet kampa girer
	flag_wait("sovyet_kampta");
	for (t = 0; t < 60 && !flag("kamp_temiz"); t++)
	{
		wait 4;
		test_oldur();
	}
	flag_wait("kamp_temiz");
	for (t = 0; t < 200 && !flag("karsi_bitti"); t++)
	{
		wait 3;
		test_oldur();
	}
	flag_wait("karsi_bitti");
	wait 4;
	for (n = 1; n <= 3; n++)
	{
		wait 2;
		getent("bomba_tetik" + n, "targetname") notify("trigger");
	}
	flag_wait("bomba_kuruldu");
	wait 1;
	level.player setorigin(zemin_bul(level.guvenli));
	flag_wait("patladi");
	wait 6;
	test_yaz("patlama tamam, leonov=" + isalive(level.leonov) + " kamptaki axis+allies=" + kamp_canli());
}

kamp_canli()
{
	n = 0;
	ai = getaiarray();
	for (i = 0; i < ai.size; i++)
		if (kamp_icinde(ai[i].origin))
			n++;
	return n;
}

test_durum()
{
	for (;;)
	{
		wait 5;
		setcvar("kr_durum", level.asama + " axis=" + getaiarray("axis").size + " allies=" + getaiarray("allies").size + " kapi=" + canli_say(level.kapi_ai) + " ic=" + canli_say(level.ic_ai) + " karsi=" + canli_say(level.karsi_ai) + " ekip0_kamyon=" + ekip_uzaklik());
	}
}

ekip_uzaklik()
{
	if (!isdefined(level.ekip) || !isdefined(level.k) || !isdefined(level.k[2]))
		return -1;
	for (i = 0; i < level.ekip.size; i++)
		if (isalive(level.ekip[i]))
			return int(distance(level.ekip[i].origin, level.k[2].origin));
	return -1;
}

test_olumsuz()
{
	for (;;)
	{
		level.player.health = 1000;
		wait 0.5;
	}
}

test_oldur()
{
	ai = getaiarray("axis");
	for (i = 0; i < ai.size; i++)
		if (isalive(ai[i]))
			ai[i] dodamage(ai[i].health + 100, ai[i].origin);
}

// --------------------------------------------------------------------------
// EKRAN TURU (kr_tur 1): kus bakisi + kritik noktalar (skill visual-qa)
// --------------------------------------------------------------------------
ekran_turu()
{
	level.player takeallweapons();
	level thread test_olumsuz();             // isinlanmada dusme hasari olduruyordu
	n = [];
	a = [];
	n[n.size] = (2950, 2250, 2600);  a[a.size] = (89, 90, 0);   // kamp ustten
	n[n.size] = (2300, 1100, 200);  a[a.size] = (4, 90, 0);   // kamp kapisi dis
	n[n.size] = (1950, 1300, 200);  a[a.size] = (6, 60, 0);   // sol kule
	n[n.size] = (2650, 1300, 200);  a[a.size] = (6, 120, 0);   // sag kule
	n[n.size] = (1900, 1600, 160);  a[a.size] = (2, 0, 0);   // sol kule merdiven yandan
	n[n.size] = (2700, 1600, 160);  a[a.size] = (2, 180, 0);   // sag kule merdiven yandan
	n[n.size] = (2880, 1600, 120);  a[a.size] = (0, 180, 0);   // sag kule merdiven karsidan
	n[n.size] = (2540, 1610, 290);  a[a.size] = (25, 270, 0);   // kule platformu ustten
	n[n.size] = (2300, 1700, 100);  a[a.size] = (4, 90, 0);   // kapi ici
	n[n.size] = (2380, 2210, 110);  a[a.size] = (4, 180, 0);   // baraka A dogu kapi
	n[n.size] = (1950, 2220, 100);  a[a.size] = (4, 0, 0);   // baraka A ic
	n[n.size] = (3375, 2690, 90);  a[a.size] = (4, 90, 0);   // depo A kapi
	n[n.size] = (3300, 2860, 110);  a[a.size] = (10, 90, 0);   // depo A ic + bomba
	n[n.size] = (3000, 1800, 120);  a[a.size] = (2, 90, 0);   // merkez bina kapi on
	n[n.size] = (2750, 2200, 110);  a[a.size] = (4, 20, 0);   // merkez zemin ic
	n[n.size] = (3000, 2150, 100);  a[a.size] = (6, 90, 0);   // merkez masa radyo kuzeye
	n[n.size] = (2900, 2300, 110);  a[a.size] = (2, 60, 0);   // dolaplar kuzey duvar
	n[n.size] = (3300, 2250, 270);  a[a.size] = (4, 30, 0);   // merkez ust kat dolap
	n[n.size] = (3040, 2160, 100);  a[a.size] = (10, 0, 0);   // bomba 1
	n[n.size] = (3150, 2200, 100);  a[a.size] = (2, 90, 0);   // ic kapi
	n[n.size] = (1850, 900, 180);  a[a.size] = (4, 60, 0);   // guvenli alan
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

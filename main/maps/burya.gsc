// burya.gsc -- "Operation Snowstorm / Kar Firtinasi", 2 Subat 1943 (metel'in devami).
//
// AKIS (senaryo + kullanici kararlari):
//   1) KONVOY: oyuncu 2. kamyonun kasasinda (stok beltot tag_player kalibi),
//      Leonov + 6 asker kasada. 3 kamyon 15 mph ~25 sn gider.
//   2) PUSU: ondeki kamyon mayina basip patlar; kamyonlar durur, herkes iner;
//      tam 10 Alman ormandan gelir.
//   3) KAMP: kampa ilerle; giris (9 + 2 MG42 kulede) dusunce giris savunmasi:
//      2 karsi saldiri (6, 8 sn sonra 8); 2 Sovyet kamyonu (7+7) gelir.
//   4) Kamp ici (10) + merkez bina (5) temizlenir; Leonov'un emri.
//   5) BOMBA: merkez binaya TNT (stok demolition kalibi); 15 sn kronometre +
//      tik (stok _bombs); oyuncu guvenli alana varinca bina patlar (basarisizlik
//      yok). Duman, ates, oksuruk; ekip toplanir, Leonov konusur, 7 sn kararma.
// Kaliplar: beltot (oyuncu kamyonda), decoytown (kamyondan inme), rhine
// (araci patlatma), demolition (TNT, bina yikimi), _bombs (kronometre),
// _spawner use_a_turret (MG42), metel (ekip beyni, yolcu dogurma, takviye).
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

	level.campaign = "russian";
	level.totalfriends = 0;                     // _load'dan ONCE (krasnoye olcusu)
	level.maxfriendlies = 0;
	maps\_truck::main("xmodel/vehicle_opel_blitz_snow");
	maps\burya_fx::main();
	maps\_load::main();
	maps\burya_anim::main();

	level.friendlyMethod = "friendly chains";
	level.player setfriendlychain(getnode("fc_baslangic", "targetname"));
	level.ekip_mod = "bekle";
	level.hucum_siper = [];

	flag_init("konvoy_vuruldu");
	flag_init("indik");
	flag_init("pusu_temiz");
	flag_init("kamp_dis_temiz");
	flag_init("takviye_indi");
	flag_init("kamp_temiz");
	flag_init("bomba_kuruldu");
	flag_init("patladi");
	flag_init("bitti");

	level.sinir = maps\burya_sinir::cokgen();
	level.bina_saglam = getent("bina_saglam", "targetname");
	level.bina_saglam moveto(level.bina_saglam.origin + (9000, 0, 0 - 2000), 0.05);   // derlemede uzakta
	level.bina_yikik = getent("bina_yikik", "targetname");
	level.bina_yikik hide();                    // +2000'de; patlamada inip gorunur
	level.bina_yikik notsolid();
	level.patlama_yeri = getent("patlama", "targetname").origin;
	level.kamp_kapi = getent("kamp_kapi", "targetname").origin;
	level.guvenli = getent("guvenli", "targetname").origin;

	if (getcvar("kr_tur") != "" && getcvar("kr_tur") != "0")
	{
		level thread ekran_turu();
		return;
	}

	oyuncu_techizat();
	siper_onbellek();
	anim.noWeaponToss = true;
	level thread ekip_beyni();
	level thread gorevler();
	if (getcvar("kr_test") == "1")
		level thread otomatik_test();
}

// --------------------------------------------------------------------------
// TANITIM: siyah perde 3 sn'de acilir (perde acilirken konvoy kalkar)
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
	wait 3;
	level notify("perde_aciliyor");
	level.introblack fadeOverTime(3);
	level.introblack.alpha = 0;
	maps\_introscreen::introscreen_fadeOutText();
	level notify("tanitim_bitti");
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
	level.asama = "FIRST_ENCOUNTER";
	level thread leonov_der("pusu");
	ekip_hucum(level.patlama_yeri, 900);
	waittill_aigroupcleared("pusu");
	flag_set("pusu_temiz");
	objective_state(2, "done");
	autoSaveByName("pusu_bitti");

	// --- KAMPA ILERLE
	level.asama = "ADVANCE_TO_CAMP";
	level.ekip_mod = "takip";
	level thread muzik("burya_muzik_yolculuk");
	leonov_der("ilerle");
	objective_add(3, "active", &"BURYA_OBJ_KAMP", level.kamp_kapi);
	objective_current(3);
	while (distance(level.player.origin, level.kamp_kapi) > 1900)
		wait 0.5;

	// --- KAMP GIRISI (dis savunma + 2 MG42)
	level.asama = "CAMP_ASSAULT";
	objective_state(3, "done");
	objective_add(4, "active", &"BURYA_OBJ_GIRIS", level.kamp_kapi);
	objective_current(4);
	autoSaveByName("kamp_girisi");
	level thread muzik("burya_muzik_kamp");
	kamp_dis_dogur();
	level thread leonov_der("kamp");
	ekip_hucum(level.kamp_kapi + (0, -500, 0), 800);
	wait 6;
	level thread leonov_der("mg");
	waittill_aigroupcleared("kamp_dis");
	flag_set("kamp_dis_temiz");
	objective_state(4, "done");
	autoSaveByName("giris_alindi");

	// --- GIRIS SAVUNMASI + TAKVIYE
	level.asama = "WAIT_FOR_REINFORCEMENTS";
	objective_add(5, "active", &"BURYA_OBJ_SAVUN", level.kamp_kapi);
	objective_current(5);
	level thread muzik("burya_muzik_savunma");
	leonov_der("savun");
	ekip_hucum(level.kamp_kapi + (0, 100, 0), 600);
	level.dalga_ai = [];
	dalga(6);
	wait 8;
	level thread leonov_der("saldiri");
	dalga(8);
	wait 10;
	level thread takviye();
	flag_wait("takviye_indi");
	while (canli_say(level.dalga_ai) > 0)
		wait 1;
	objective_state(5, "done");
	autoSaveByName("takviye_geldi");

	// --- KAMPI ELE GECIR (ic 10 + merkez 5)
	level.asama = "CAPTURE_CAMP";
	objective_add(6, "active", &"BURYA_OBJ_ELE", (2950, 2300, 40));
	objective_current(6);
	level thread muzik("burya_muzik_kamp");
	level thread leonov_der("temizle");
	grup_dogur("kamp_ic");
	grup_dogur("kamp_merkez");
	ekip_hucum((2950, 2250, 40), 1300);
	waittill_aigroupcleared("kamp_ic");
	waittill_aigroupcleared("kamp_merkez");
	kalan_almanlari_bitir();
	flag_set("kamp_temiz");
	objective_state(6, "done");
	autoSaveByName("kamp_temiz");

	// --- LEONOV'UN EMRI
	level.asama = "CAPTURE_CAMP_DONE";
	level.ekip_mod = "bekle";
	ekip_git((3000, 1830, 40), 220);
	objective_add(7, "active", &"BURYA_OBJ_BEKLE", (3000, 1830, 40));
	objective_current(7);
	level thread muzik("burya_muzik_yolculuk");
	leonov_der("kamp_bizde");
	for (t = 0; t < 40 && distance(level.player.origin, level.leonov.origin) > 350; t++)
		wait 0.5;
	objective_state(7, "done");

	// --- BOMBA
	level.asama = "PLANT_EXPLOSIVE";
	bombalar = getentarray("bomba", "targetname");
	b = bombalar[0];
	for (i = 0; i < bombalar.size; i++)
		if (bombalar[i].script_noteworthy == "1")
			b = bombalar[i];
	objective_add(8, "active", &"BURYA_OBJ_BOMBA", b.origin);
	for (i = 0; i < bombalar.size; i++)
		objective_additionalposition(8, i, bombalar[i].origin);
	objective_current(8);
	leonov_der("bomba");
	level.kurulan = 0;
	for (i = 0; i < bombalar.size; i++)
		bombalar[i] thread bomba_kur(i);
	while (level.kurulan < bombalar.size)
		wait 0.2;
	flag_set("bomba_kuruldu");
	objective_state(8, "done");
	autoSaveByName("bomba");

	// --- KACIS
	level.asama = "ESCAPE";
	objective_add(9, "active", &"BURYA_OBJ_KAC", level.guvenli);
	objective_current(9);
	level thread muzik_bir("burya_muzik_bomba");
	level.ekip_mod = "bekle";
	ekip_git(level.guvenli, 260);
	level thread kacis_replikleri();
	sayac = maps\_utility::getstopwatch(60, 15);
	b playloopsound("bomb_tick");
	bas = gettime();
	sure_doldu = false;
	for (;;)
	{
		if (!sure_doldu && gettime() - bas >= 15000)
		{
			sure_doldu = true;
			sayac destroy();
		}
		if (sure_doldu && distance(level.player.origin, level.guvenli) < 400)
			break;
		wait 0.1;
	}
	b stoploopsound();

	// --- PATLAMA
	level.asama = "FINAL_EXPLOSION";
	bina_patlat(b, bombalar);
	objective_state(9, "done");
	level thread muzik_bir("burya_muzik_final");
	wait 5;
	oksuruk();

	// --- GOREV SONU
	level.asama = "MISSION_COMPLETE";
	objective_add(10, "active", &"BURYA_OBJ_LEONOV", level.guvenli);
	objective_current(10);
	final_toplan(level.guvenli);
	for (t = 0; t < 80; t++)
	{
		if (distance(level.player.origin, level.leonov.origin) < 230 && (toplandi() || t > 40))
			break;
		wait 0.5;
	}
	objective_state(10, "done");
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
			r.ekip_uyesi = true;
			if (isdefined(r.script_noteworthy) && r.script_noteworthy == "leonov")
				level.leonov = r;
			level.ekip[level.ekip.size] = r;
		}
	}
	if (isdefined(level.leonov))
	{
		level.leonov.animname = "leonov";
		level.leonov thread magic_bullet_shield();
		level.leonov.dontavoidplayer = true;
	}
	test_yaz("konvoy yolcu: k2=" + yolcu_say(level.k[2]) + " k3=" + yolcu_say(level.k[3]) + " k1=" + yolcu_say(level.k[1]) + " leonov=" + isdefined(level.leonov));
	// oyuncu 2. kamyonun kasasinda (stok beltot.gsc:1613)
	k2 = level.k[2];
	level.player setorigin(k2 gettagorigin("tag_player"));
	level.player setplayerangles(k2.angles);
	level.player playerLinkToDelta(k2, "tag_player", 0.1);
	level.player allowProne(false);
	level.player allowLeanLeft(false);
	level.player allowLeanRight(false);
	level waittill("perde_aciliyor");
	level.konvoy_bas = gettime();
	for (g = 1; g <= 3; g++)
		level thread maps\_vehicle::gopath(level.k[g]);
	level thread muzik("burya_muzik_yolculuk");
	level.k[3] thread on_kamyon_patla();       // kullanici: arkadaki kamyon kopru ustunde patlar
	wait 5;
	leonov_der("giris");
	k2 waittill("reached_end_node");
	wait 1.2;
	oyuncu_in(k2);
	flag_set("indik");
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
	if (isdefined(self.riders))
		for (i = 0; i < self.riders.size; i++)
			if (isalive(self.riders[i]))
				self.riders[i] dodamage(self.riders[i].health + 50, org);
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
	for (i = 0; i < level.ekip.size; i++)
		if (isalive(level.ekip[i]))
			level.ekip[i].ignoreall = false;
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
// TAKVIYE: 2 Sovyet kamyonu, her birinde 7 kisi (sofor + 6)
// --------------------------------------------------------------------------
takviye()
{
	iprintlnbold(&"BURYA_MSG_TAKVIYE");
	level thread asker_der("takviye");
	level thread takviye_kamyonu(4, "takviye1", level.kamp_kapi + (-200, 100, 0));
	wait 5;
	level thread takviye_kamyonu(5, "takviye2", getent("yan_kapi", "targetname").origin);
	wait 25;
	flag_set("takviye_indi");
}

takviye_kamyonu(grup, ad, hedef)
{
	arac_yolcu_hazirla(grup, ad, 24);
	a = maps\_vehicle::scripted_spawn(grup);
	k = a[0];
	k thread arac_olumsuz();
	level thread maps\_vehicle::gopath(k);
	if (!isdefined(k.riders))
		return;
	yolcu = k.riders;
	test_yaz("takviye " + ad + " yolcu=" + canli_say(yolcu));
	k waittill("reached_end_node");
	wait 6;
	for (i = 0; i < yolcu.size; i++)
	{
		g = yolcu[i];
		if (!isalive(g))
			continue;
		g thread takviye_askeri(hedef);
	}
}

takviye_askeri(hedef)
{
	self endon("death");
	self.pathenemyfightdist = 700;
	self.pathenemylookahead = 700;
	self.goalradius = 300;
	self setgoalpos(zemin_bul(hedef));
	self hedef_bekle(25);
	self bolge_dolas((2950, 2250, 0), 1300, -9999, 9999);
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

grup_dogur(ad)
{
	sp = getentarray(ad, "targetname");
	for (i = 0; i < sp.size; i++)
	{
		g = dogur(sp[i]);
		sp[i] delete();
		if (!isdefined(g))
			continue;
		if (ad == "pusu")
			g thread bolge_dolas(level.patlama_yeri + (250, 300, 0), 850, -9999, 9999);
		else if (ad == "kamp_dis")
			g thread bolge_dolas(level.kamp_kapi + (0, 200, 0), 700, -9999, 9999);
		else if (ad == "kamp_ic")
			g thread bolge_dolas((2950, 2300, 0), 1150, -9999, 9999);
		else
			g thread bolge_dolas((3000, 2300, 0), 480, -9999, 9999);
		wait 0.1;
	}
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
		g allowedstances("prone");
		g thread mg_kalk(en);
	}
	grup_dogur("kamp_dis");
}

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
	self allowedstances("stand", "crouch", "prone");
	wait 0.8;
	self useturret(mg);                         // stok _spawner use_a_turret
	mg setmode("auto_ai");
}

// karsi saldiri dalgasi: kampin kuzeyinden (depolarin arkasi, gorus disi)
dalga(adet)
{
	sp = getentarray("dalga", "targetname");
	for (i = 0; i < adet; i++)
	{
		g = dogur(sp[i % sp.size]);
		if (!isdefined(g))
			continue;
		level.dalga_ai[level.dalga_ai.size] = g;
		g thread dalga_alman();
		wait 0.4;
	}
}

dalga_alman()
{
	self endon("death");
	self.pathenemyfightdist = 700;
	self.pathenemylookahead = 700;
	self.goalradius = 350;
	self setgoalpos(zemin_bul(level.kamp_kapi + (0, 350, 0)));
	self hedef_bekle(25);
	self bolge_dolas(level.kamp_kapi + (0, 200, 0), 650, -9999, 9999);
}

kalan_almanlari_bitir()
{
	// gorev kapsamindaki gruplar bitti; dalgadan kalan varsa beklenir
	for (t = 0; t < 60 && canli_say(level.dalga_ai) > 0; t++)
		wait 1;
}

canli_say(liste)
{
	n = 0;
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
			wait randomfloatrange(7, 14);
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
				if (isalive(level.ekip[i]))
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

// ekip bir noktaya (yarim cember) gider ve orada bekler
ekip_git(merkez, yaricap)
{
	level.ekip_mod = "bekle";
	n = 0;
	for (i = 0; i < level.ekip.size; i++)
	{
		g = level.ekip[i];
		if (!isalive(g))
			continue;
		a = 360.0 * n / 8;
		n++;
		g.goalradius = 64;
		g setgoalpos(zemin_bul(merkez + (cos(a) * yaricap, sin(a) * yaricap, 0)));
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
// BOMBA (stok demolition.gsc:1666-1724) VE BINA YIKIMI (demolition buildingExplodes)
// --------------------------------------------------------------------------
bomba_kur(no)
{
	t = getent(self.target, "targetname");
	t sethintstring(&"BURYA_PLATFORM_BOMBA_KUR");
	t waittill("trigger");
	t delete();
	self setmodel("xmodel/military_tntbomb");
	self playsound("explo_plant_no_tick");
	objective_additionalposition(8, no, (0, 0, 0));
	level.kurulan++;
	test_yaz("patlayici kuruldu: " + level.kurulan);
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

bina_patlat(b, bombalar)
{
	flag_set("patladi");
	test_yaz("KAMP PATLADI");
	fx = getentarray("bina_fx", "targetname");
	merkez = (3000, 2300, 60);
	ses = spawn("script_origin", merkez + (0, 0, 200));
	ses playsound("demolition_demoexplosion");
	earthquake(0.35, 4, merkez, 7000);
	// depo ve baraka patlayicilari once (zincirleme)
	for (i = 0; i < bombalar.size; i++)
	{
		if (bombalar[i] == b)
			continue;
		o = bombalar[i].origin;
		playfx(level._effect["bina_buyuk"], o + (0, 0, 40));
		playfx(level._effect["mayin"], o);
		s2 = spawn("script_origin", o + (0, 0, 100));
		s2 playsound("explo_mine");
		radiusDamage(o, 500, 800, 400);
		maps\_fx::loopfx("bina_ates", o + (0, 0, 20), 0.6);
		maps\_fx::loopfx("bina_duman", o + (0, 0, 120), 1.5);
		bombalar[i] delete();
		wait 0.4;
	}
	for (i = 0; i < fx.size; i++)
	{
		playfx(level._effect["bina_taban"], fx[i].origin);
		wait randomfloatrange(0.05, 0.2);
	}
	playfx(level._effect["bina_buyuk"], merkez + (0, 0, 120));
	playfx(level._effect["bina_pencere"], (3000, 1975, 110));
	playfx(level._effect["bina_pencere"], (2650, 1975, 250));
	playfx(level._effect["bina_pencere"], (3350, 2625, 250));
	playfx(level._effect["bina_toz"], merkez);
	earthquake(0.5, 1.2, merkez, 7000);
	radiusDamage(merkez, 900, 1000, 900);
	esya = getentarray("bina_esya", "targetname");
	for (i = 0; i < esya.size; i++)
		esya[i] delete();
	b delete();
	level.bina_saglam delete();
	level.bina_yikik moveto(level.bina_yikik.origin + (9000, 0, 0 - 2000), 0.05);
	wait 0.1;
	level.bina_yikik show();
	level.bina_yikik solid();
	ses playsound("demolition_building_collapse");
	wait 0.5;
	playfx(level._effect["bina_sutun"], merkez + (-250, 0, 0));
	playfx(level._effect["bina_sutun"], merkez + (250, 0, 0));
	earthquake(0.3, 6, merkez, 7000);
	wait 2;
	maps\_fx::loopfx("bina_toz_son", merkez, 6);
	maps\_fx::loopfx("bina_ates", merkez + (-300, -120, 30), 0.6);
	maps\_fx::loopfx("bina_ates", merkez + (260, 140, 30), 0.6);
	maps\_fx::loopfx("bina_duman", merkez + (0, 0, 80), 1.5);
	maps\_fx::loopfx("bina_ates", (2100, 2210, 160), 0.7);      // baraka catisi
	maps\_fx::loopfx("bina_ates", (3375, 2860, 170), 0.7);      // depo catisi
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
// SES / MUZIK
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
	for (t = 0; t < 70; t++)                    // en fazla 7 sn beklenir
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
		g playsound("burya_leonov_" + replik, "soyledi");
		g waittill_any_timeout_burya(7, "soyledi", "death");
		if (isalive(g))
			g setBattleChatter(true);
	}
	level.replik_bitti = no;
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
	konusan playsound("burya_asker_" + ad, "replik_bitti");
	konusan waittill("replik_bitti");
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
	flag_wait("konvoy_vuruldu");
	wait 3;
	test_yaz("pusu dogdu: axis=" + getaiarray("axis").size);
	wait 6;
	test_oldur();
	flag_wait("pusu_temiz");
	test_yaz("pusu temiz");
	wait 3;
	level.player setorigin(zemin_bul(level.kamp_kapi + (0, -1500, 0)));
	wait 6;
	test_yaz("kamp dis axis=" + getaiarray("axis").size);
	test_oldur();
	flag_wait("kamp_dis_temiz");
	test_yaz("kamp dis temiz");
	for (t = 0; t < 30; t++)
	{
		wait 3;
		test_oldur();
	}
	flag_wait("takviye_indi");
	test_yaz("takviye indi: allies=" + getaiarray("allies").size);
	for (t = 0; t < 20 && !flag("kamp_temiz"); t++)
	{
		wait 4;
		test_yaz("kamp ici axis=" + getaiarray("axis").size);
		test_oldur();
	}
	flag_wait("kamp_temiz");
	test_yaz("kamp temiz");
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
	test_yaz("patlama tamam, leonov=" + isalive(level.leonov));
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
	n = [];
	a = [];
	n[n.size] = (0, -100, 5200);  a[a.size] = (89, 90, 0);   // tum harita
	n[n.size] = (2950, 2250, 2600);  a[a.size] = (89, 90, 0);   // kamp ustten
	n[n.size] = (300, -200, 1800);  a[a.size] = (89, 90, 0);   // kopru+pusu ustten
	n[n.size] = (-4000, -2600, 240);  a[a.size] = (4, 30, 0);   // baslangic ileri
	n[n.size] = (-4000, -2600, 240);  a[a.size] = (4, 210, 0);   // baslangic geri vadi
	n[n.size] = (-2600, -1900, 220);  a[a.size] = (4, 30, 0);   // yol 1
	n[n.size] = (-1200, -1050, 220);  a[a.size] = (4, 30, 0);   // yol 2 kule
	n[n.size] = (-1960, -1100, 200);  a[a.size] = (4, 90, 0);   // dekor kule yakin
	n[n.size] = (-250, -424, 170);  a[a.size] = (4, 0, 0);   // kopru bati
	n[n.size] = (700, -300, 170);  a[a.size] = (4, 180, 0);   // kopru dogu
	n[n.size] = (650, -150, 200);  a[a.size] = (4, 45, 0);   // pusu alani
	n[n.size] = (1500, 700, 230);  a[a.size] = (4, 60, 0);   // kampa yol
	n[n.size] = (2300, 900, 220);  a[a.size] = (4, 90, 0);   // kamp kapisi dis
	n[n.size] = (2300, 1420, 200);  a[a.size] = (10, 90, 0);   // kapi yakin
	n[n.size] = (1950, 1450, 260);  a[a.size] = (15, 60, 0);   // sol kule
	n[n.size] = (2650, 1450, 260);  a[a.size] = (15, 120, 0);   // sag kule
	n[n.size] = (2540, 1450, 330);  a[a.size] = (25, 90, 0);   // kule MG siperi
	n[n.size] = (2800, 1600, 200);  a[a.size] = (10, 180, 0);   // kule merdiveni
	n[n.size] = (2300, 1750, 200);  a[a.size] = (4, 90, 0);   // kapi ici
	n[n.size] = (2100, 1950, 150);  a[a.size] = (4, 40, 0);   // baraka A dis
	n[n.size] = (1950, 2220, 100);  a[a.size] = (4, 0, 0);   // baraka A ic
	n[n.size] = (2100, 2420, 150);  a[a.size] = (4, 90, 0);   // baraka B dis
	n[n.size] = (3650, 1900, 150);  a[a.size] = (4, 10, 0);   // baraka C dis
	n[n.size] = (3650, 2550, 150);  a[a.size] = (4, 10, 0);   // baraka D dis
	n[n.size] = (2650, 2700, 150);  a[a.size] = (4, 90, 0);   // depo B dis
	n[n.size] = (3375, 2700, 150);  a[a.size] = (4, 90, 0);   // depo A dis
	n[n.size] = (3300, 2860, 110);  a[a.size] = (10, 90, 0);   // depo A ic + bomba
	n[n.size] = (3000, 1800, 200);  a[a.size] = (2, 90, 0);   // merkez bina dis on
	n[n.size] = (3700, 2300, 200);  a[a.size] = (2, 180, 0);   // merkez bina dis dogu
	n[n.size] = (2750, 2200, 110);  a[a.size] = (4, 20, 0);   // merkez zemin ic
	n[n.size] = (3040, 2160, 100);  a[a.size] = (10, 0, 0);   // bomba 1
	n[n.size] = (2580, 2060, 110);  a[a.size] = (8, 90, 0);   // merdiven
	n[n.size] = (3300, 2250, 270);  a[a.size] = (4, 200, 0);   // merkez ust kat
	n[n.size] = (1930, 2150, 110);  a[a.size] = (10, 180, 0);   // bomba 3 baraka
	n[n.size] = (3400, -500, 200);  a[a.size] = (4, 40, 0);   // karakol dekor
	n[n.size] = (3700, 600, 200);  a[a.size] = (4, 0, 0);   // takviye yolu ucu
	n[n.size] = (1850, 900, 180);  a[a.size] = (4, 60, 0);   // guvenli alan
	n[n.size] = (300, -1500, 220);  a[a.size] = (4, 300, 0);   // dere guney ucu
	n[n.size] = (-600, 1300, 260);  a[a.size] = (4, 100, 0);   // dere kuzey ucu
	n[n.size] = (2600, -700, 200);  a[a.size] = (4, 300, 0);   // orman yolu ucu
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

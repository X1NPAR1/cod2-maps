// kumtepe.gsc -- "Operation Sandstorm", Kum Tepe, El Alamein, 24 Ekim 1942 (burya'nin devami).
//
// AKIS (kullanici kararlari):
//   1) KAMYON: oyuncu kasada, Cpt. Price (olumsuz) + 7 Ingiliz; ~20 sn, catisma koyde basladi.
//   2) KOY: 15 Alman (pencereler, cati, avlu) temizlenir.
//   3) SAVUNMA: herkes pencere arkalarina / catiya; 30 sn'de bir 10 Alman, toplam 60
//      (kuzey, guney, bati tepelerinin arkasindan; once duman).
//   4) TANKLAR: 60'i da olunce 25 sn sonra 4 Panzer II, 5 sn arayla batidan dort
//      seritte, arkalarinda toplam 30 Alman. Oyuncunun tanksavari yok: hayatta kal.
//   5) KURTULUS: piyade bitince gorunmeyen yerden (gelinen yoldan) 4 Crusader. Biri
//      1 can: bir Panzer onu vurur, patlar. Sonra Crusaderlar Panzerleri patlatir.
//   6) 20 Ingiliz yaya gelip koyde siper alir; Price'in zafer sozleri, jenerik.
// Kaliplar: burya (konvoy, gorunmez dogus, pencere siperleri, kosarak saldiri),
// duhoc_defend (tank: setturrettargetent -> turret_on_target -> turret_fire), rhine.
#include maps\_utility;
#include maps\_anim;

main()
{
	setExpFog(0.00034, .80, .62, .44, 0);       // kullanici: aksam, kumlu ve hafif sisli
	setCullDist(16000);

	precacheString(&"KUMTEPE_OBJ_YOL");
	precacheString(&"KUMTEPE_OBJ_KOY");
	precacheString(&"KUMTEPE_OBJ_SAVUN");
	precacheString(&"KUMTEPE_OBJ_TANK");
	precacheString(&"KUMTEPE_OBJ_PRICE");
	precacheString(&"KUMTEPE_MSG_CRUSADER");
	precacheString(&"KUMTEPE_INTRO_TITLE");
	precacheString(&"KUMTEPE_INTRO_PLACE");
	precacheString(&"KUMTEPE_INTRO_DATE");
	precacheString(&"KUMTEPE_INTRO_INFO");
	precacheShader("black");
	precacheString(&"KUMTEPE_OBJ_TELSIZ");
	precacheString(&"KUMTEPE_PLATFORM_TELSIZ");
	precacheModel("xmodel/military_german_fieldradio_green");
	precacheModel("xmodel/vehicle_stuka_flying");
	precacheModel("xmodel/prop_stuka_bomb");
	precacheModel("xmodel/egypt_prop_buildingpiece01");
	precacheModel("xmodel/egypt_prop_buildingpiece02");
	precacheModel("xmodel/egypt_prop_buildingpiece03");
	precacheModel("xmodel/egypt_prop_buildingpiece04");
	precacheModel("xmodel/military_german_fieldradio_green_obj");

	level.campaign = "british";
	level.totalfriends = 0;                     // _load'dan ONCE (krasnoye olcusu)
	level.maxfriendlies = 0;
	maps\_truck::main("xmodel/vehicle_opel_blitz_desert");
	maps\_crusader::main("xmodel/vehicle_crusader2");
	maps\_panzer2::main("xmodel/vehicle_panzer_ii");
	maps\_halftrack::main("xmodel/vehicle_halftrack_mg_desert");
	maps\kumtepe_fx::main();
	maps\_load::main();
	maps\kumtepe_anim::main();

	level.ekip_mod = "bekle";
	level.hucum_siper = [];
	flag_init("kalk");
	flag_init("tanitim_bitti");
	flag_init("indik");
	flag_init("koy_temiz");
	flag_init("koy_dogdu");
	flag_init("savunma_bitti");
	flag_init("piyade_bitti");
	flag_init("bitti");

	level.sinir = maps\kumtepe_sinir::cokgen();
	// koy karesi (kullanici): inince koyden cikilmaz
	level.koy_kare = [];
	level.koy_kare[0] = (-1590, -1590, 0);
	level.koy_kare[1] = (1590, -1590, 0);
	level.koy_kare[2] = (1590, 1590, 0);
	level.koy_kare[3] = (-1590, 1590, 0);
	// derlemede uzakta duran ust kat yarisi yerine konur; enkazi gizli
	level.ust_bati = getent("ust_bati", "targetname");
	level.ust_bati moveto(level.ust_bati.origin + (5120, 0, 0 - 2048), 0.05);
	level.ust_dogu = getent("ust_dogu", "targetname");
	level.ust_dogu moveto(level.ust_dogu.origin + (5120, 0, 0 - 2048), 0.05);
	level.kose = getent("kapali_kose", "targetname");
	level.kose moveto(level.kose.origin + (5120, 0, 0 - 2048), 0.05);
	level.kose_harabe = getent("kapali_kose_harabe", "targetname");
	level.kose_harabe hide();
	level.kose_harabe notsolid();
	level.harabe = getent("ikikat_harabe", "targetname");
	level.harabe hide();
	level.harabe notsolid();
	level.ust_yikik = getent("ust_bati_yikik", "targetname");
	level.ust_yikik hide();
	level.ust_yikik notsolid();
	t = getent("telsiz_tetik", "targetname");
	t.eski = t.origin;
	t.origin = t.origin + (0, 0, 0 - 10000);
	level.koy = getent("koy_orta", "targetname").origin;
	level.inis = getent("inis", "targetname").origin;
	level.asama = "BASLANGIC";

	if (getcvar("kr_tur") != "" && getcvar("kr_tur") != "0")
	{
		level thread ekran_turu();
		return;
	}

	oyuncu_techizat();
	siper_onbellek();
	anim.noWeaponToss = true;
	level.ekip = [];
	level.ingilizler = [];
	level thread ekip_beyni();
	level thread gorevler();
}

// --------------------------------------------------------------------------
// TANITIM: kamyon perde bitmeden ~2 sn once hareketli gorunur (burya olcusu:
// kalkis emri ile gorunur hareket arasinda 2-3 sn var)
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
	musicplay("kumtepe_muzik_giris");
	wait .05;
	level.introstring = [];
	maps\_introscreen::introscreen_create_line(&"KUMTEPE_INTRO_TITLE");
	wait 2;
	maps\_introscreen::introscreen_create_line(&"KUMTEPE_INTRO_PLACE");
	maps\_introscreen::introscreen_create_line(&"KUMTEPE_INTRO_DATE");
	wait 2;
	maps\_introscreen::introscreen_create_line(&"KUMTEPE_INTRO_INFO");
	wait 1;
	flag_set("kalk");
	wait 2;
	level.introblack fadeOverTime(3);
	level.introblack.alpha = 0;
	maps\_introscreen::introscreen_fadeOutText();
	flag_set("tanitim_bitti");
}

// kullanici: Lee-Enfield + Thompson (+ el bombasi, duman)
oyuncu_techizat()
{
	level.player takeallweapons();
	level.player giveWeapon("enfield");
	level.player giveWeapon("thompson");
	level.player giveWeapon("MK1britishfrag");
	level.player giveWeapon("smoke_grenade_american");
	level.player giveMaxAmmo("enfield");
	level.player giveMaxAmmo("thompson");
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
	level.asama = "CONVOY";
	objective_add(1, "active", &"KUMTEPE_OBJ_YOL", level.inis);
	objective_current(1);
	level thread uzak_catisma();
	kamyon();

	// --- KOY
	level.asama = "ASSAULT_VILLAGE";
	objective_state(1, "done");
	objective_add(2, "active", &"KUMTEPE_OBJ_KOY", level.koy);
	objective_current(2);
	level thread muzik("kumtepe_muzik_koy");
	level thread price_der("hucum");
	ekip_hucum(level.koy, 1200);
	flag_wait("koy_dogdu");                         // olculdu: grup dogmadan bos sayiliyordu
	while (canli_say(level.koy_ai) > 0)
		wait 0.5;
	flag_set("koy_temiz");
	level notify("uzak_catisma_dur");
	objective_state(2, "done");
	level thread autoSaveByName("koy_alindi");

	// --- SAVUNMA: 30 sn'de bir 10 Alman, toplam 60
	level.asama = "DEFEND";
	objective_add(3, "active", &"KUMTEPE_OBJ_SAVUN", level.koy);
	objective_current(3);
	level thread muzik("kumtepe_muzik_savunma");
	price_der("savun");
	savunmaya_gec(tum_ingilizler());
	wait 10;                                        // kullanici: temizlikten ~10 sn sonra
	level.dalga_ai = [];
	for (d = 0; d < 6; d++)
	{
		dalga_bas(d);
		if (d < 5)
			wait 30;
	}
	while (canli_say(level.dalga_ai) > 0)
		wait 1;
	flag_set("savunma_bitti");
	objective_state(3, "done");
	level thread autoSaveByName("savunma");

	// --- TANKLAR: 25 sn sonra 4 Panzer II + 30 Alman
	wait 25;
	level.asama = "TANKS";
	objective_add(4, "active", &"KUMTEPE_OBJ_TANK", level.koy);
	objective_current(4);
	level thread muzik("kumtepe_muzik_tank");
	level thread price_der("tank");
	tank_saldirisi();
	tanklar_durdu(40);
	kose_vur();
	wait 3;
	objective_state(4, "done");

	// --- TELSIZ (yildiz gorev geldigi anda): oyuncu telsiza varinca ev vurulur
	level.asama = "RADIO";
	level thread price_der("telsiz_git");
	r = getent("telsiz", "targetname");
	objective_add(5, "active", &"KUMTEPE_OBJ_TELSIZ", r.origin);
	objective_current(5);
	r thread telsiz_yanip_son();
	while (distance(level.player.origin, r.origin) > 260)
		wait 0.2;
	level thread ikikat_yikimi();
	telsiz_kullan();
	objective_state(5, "done");
	level thread autoSaveByName("telsiz");
	wait randomfloatrange(30, 50);

	// --- KURTULUS: Crusaderlar + 15 sn sonra 15 Ingiliz
	level.asama = "RELIEF";
	level thread muzik_bir("kumtepe_muzik_kurtulus");
	level thread ingiliz_takviyesi_gecikmeli(15);
	crusader_gelir();
	while (canli_say(level.tank_piyade) > 0 || getaiarray("axis").size > 0)
		wait 1;
	flag_set("piyade_bitti");
	level.asama = "REINFORCE";
	wait 4;

	// --- SON
	level.asama = "END";
	halka_kur((0, 230, 41));
	objective_add(6, "active", &"KUMTEPE_OBJ_PRICE", level.price.origin);
	objective_current(6);
	level thread price_takip_obj();
	for (t = 0; t < 120; t++)
	{
		if (distance(level.player.origin, level.price.origin) < 260)
			break;
		wait 0.5;
	}
	objective_state(6, "done");
	level thread muzik_bir("kumtepe_muzik_final");
	price_der("final1");
	price_der("final2");
	wait 3;
	if (!flag("bitti"))
	{
		flag_set("bitti");
		bolum_sonu();
	}
}

// kullanici: Price meydana cikar, etrafinda 4-5 kisilik halka; Price halkanin parcasi
halka_kur(merkez)
{
	tum = tum_ingilizler();
	uye = [];
	uye[0] = level.price;
	for (i = 0; i < tum.size && uye.size < 6; i++)
		if (tum[i] != level.price)
			uye[uye.size] = tum[i];
	for (i = 0; i < uye.size; i++)
	{
		a = 270 + 360.0 * i / (uye.size + 1);         // oyuncuya bir bosluk
		p = zemin_bul(merkez + (cos(a) * 140, sin(a) * 140, 0));
		uye[i] notify("yeni_emir");
		uye[i] allowedstances("stand");
		uye[i].goalradius = 16;
		uye[i] setgoalpos(p);
		uye[i] thread ortaya_bak(merkez);
	}
}

ortaya_bak(merkez)
{
	self endon("death");
	self hedef_bekle(15);
	m = spawn("script_origin", merkez + (0, 0, 60));
	for (t = 0; t < 120; t++)
	{
		self lookat(m, 1.2);
		wait 1;
	}
	m delete();
}

price_takip_obj()
{
	while (level.asama == "END")
	{
		objective_position(6, level.price.origin);
		wait 0.5;
	}
}

// yolculukta koyden gelen catisma sesleri / uzak patlamalar
uzak_catisma()
{
	level endon("uzak_catisma_dur");
	while (!flag("indik"))
	{
		wait randomfloatrange(1.5, 3.5);
		p = level.koy + (randomfloatrange(-900, 900), randomfloatrange(-900, 900), 40);
		playfx(level._effect["uzak_patlama"], p);
		s = spawn("script_origin", p);
		s playsound("mortar_explosion");
		s thread sil_sonra(5);
	}
}

sil_sonra(sure)
{
	wait sure;
	self delete();
}

// --------------------------------------------------------------------------
// KAMYON (stok beltot tag_player + decoytown inis)
// --------------------------------------------------------------------------
kamyon()
{
	arac_yolcu_hazirla(1, "kamyon", 30);
	a = maps\_vehicle::scripted_spawn(1);
	k = a[0];
	k thread arac_olumsuz();
	if (isdefined(k.riders))
		for (i = 0; i < k.riders.size; i++)
		{
			r = k.riders[i];
			if (!isalive(r))
				continue;
			if (isdefined(r.script_noteworthy) && r.script_noteworthy == "price")
			{
				level.price = r;
				r.animname = "price";
				r thread magic_bullet_shield();     // kullanici: Price olumsuz
				r.dontavoidplayer = true;
			}
			else
			{
				r.health = 1450;                // kullanici: 1450
				r.maxhealth = 1450;
			}
			r.ekip_uyesi = true;
			level.ekip[level.ekip.size] = r;
		}
	n = getvehiclenode(k.target, "targetname");
	if (isdefined(n) && isdefined(n.speed))
		level.kamyon_hiz = n.speed;
	level.player setorigin(k gettagorigin("tag_player"));
	level.player setplayerangles(k.angles);
	level.player playerLinkToDelta(k, "tag_player", 0.1);
	level.player allowProne(false);
	level.player allowLeanLeft(false);
	level.player allowLeanRight(false);
	flag_wait("kalk");
	level thread maps\_vehicle::gopath(k);
	level thread ucak_gecisi(k);
	level thread muzik("kumtepe_muzik_yolculuk");
	flag_wait("tanitim_bitti");
	wait 2;
	price_der("giris");
	level thread koy_yaklasinca(k);
	k waittill("reached_end_node");
	wait 1.2;
	oyuncu_in(k);
	flag_set("indik");
	price_der("inis");
	g = getent("koy_sinir", "targetname");        // kullanici: koyden cikilamaz
	if (isdefined(g))
		g moveZ(0 - 4000, 0.05);
	tum = tum_ingilizler();
	for (i = 0; i < tum.size; i++)
		tum[i] thread takili_kurtar();
}

// kullanici: baslangicta ustumuzden Stuka gecer, yolumuza dalip ates eder, yukselip
// harita disina gider; ates ettigi an kamyon 6 mph hizlanir
ucak_gecisi(k)
{
	wait 7;
	ileri = anglestoforward(k.angles);
	ileri = vectornormalize((ileri[0], ileri[1], 0));
	bas = k.origin - vectorScale(ileri, 4500) + (0, 0, 2300);
	dalis = k.origin + vectorScale(ileri, 1400) + (0, 0, 420);
	cikis = k.origin + vectorScale(ileri, 9000) + (0, 0, 2800);
	u = spawn("script_model", bas);
	u setmodel("xmodel/vehicle_stuka_flying");
	u.angles = vectortoangles(dalis - bas);
	u playsound("plane_flyby_stuka1");
	u moveto(dalis, 2.6, 0.4, 0);
	wait 2.0;
	u playloopsound("stuka_guns");
	for (i = 0; i < 14; i++)
	{
		p = k.origin + vectorScale(ileri, 500 + i * 110) + (randomfloatrange(-120, 120), randomfloatrange(-120, 120), 0);
		playfx(level._effect["kum_mermi"], zemin_bul(p));
		if (i == 4)
		{
			k thread kamyon_kacis();             // kullanici: 3 sn 20 mph, sonra 15
		}
		wait 0.07;
	}
	u stoploopsound();
	u.angles = vectortoangles(cikis - dalis);
	u moveto(cikis, 3.2, 0, 0.6);
	wait 3.3;
	u delete();
}

kamyon_kacis()
{
	self endon("reached_end_node");
	self setspeed(20, 14);
	wait 3;
	self setspeed(15, 6);
}

// kullanici: kamyon duraga 3 yol noktasi kala koydeki Almanlar doger (araçtan ates edilir)
koy_yaklasinca(k)
{
	durak = (782, 1071, 0);
	while (distance((k.origin[0], k.origin[1], 0), durak) > 760)
		wait 0.1;
	grup_dogur("koy");
}

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

// --------------------------------------------------------------------------
// SAVUNMA YERLESIMI: pencere arkalari (alt kat yurunerek), cati (gorulmeden)
// --------------------------------------------------------------------------
savunmaya_gec(liste)
{
	level.ekip_mod = "bekle";
	liste = cati_mg_nobeti(liste);
	ev1 = ev_noktalari("ikikat");
	ev2 = ev_noktalari("ev");
	liste = karistir(liste);
	// Price her zaman yikilacak (iki katli) evde
	if (isdefined(level.price) && isalive(level.price) && !isdefined(level.ikikat_yikik))
	{
		for (i = 0; i < liste.size; i++)
			if (liste[i] == level.price)
			{
				liste[i] = liste[0];
				liste[0] = level.price;
			}
	}
	for (i = 0; i < liste.size; i++)
	{
		g = liste[i];
		yer = undefined;
		if (!isdefined(level.ikikat_yikik) && (i % 2 == 0 || !ev2.size) && ev1.size)
		{
			yer = ev1[0];
			ev1 = dizi_bas_sil(ev1);
			g.oda = "ikikat";
		}
		else if (ev2.size)
		{
			yer = ev2[0];
			ev2 = dizi_bas_sil(ev2);
			g.oda = "ev";
		}
		if (!isdefined(yer))
		{
			g.oda = "ev";
			yer = getent("telsiz", "targetname");   // dolu: telsizli evin ortasina yakin
		}
		yer.dolu = true;
		g.siper_ent = yer;
		g thread siper_al(yer.origin, false);
	}
}

// evin bos noktalari: once pencereler (karisik), sonra ic noktalar
ev_noktalari(oda)
{
	pen = [];
	ic = [];
	e = getentarray("pencere", "targetname");
	for (i = 0; i < e.size; i++)
		if (e[i].script_noteworthy == oda && !isdefined(e[i].dolu))
			pen[pen.size] = e[i];
	e = getentarray("ev_ic", "targetname");
	for (i = 0; i < e.size; i++)
		if (e[i].script_noteworthy == oda && !isdefined(e[i].dolu))
			ic[ic.size] = e[i];
	pen = karistir(pen);
	ic = karistir(ic);
	for (i = 0; i < ic.size; i++)
		pen[pen.size] = ic[i];
	return pen;
}

// kullanici: catida iki MG (biri geldigimiz yola, biri tank yoluna); iki asker kullanir
cati_mg_nobeti(liste)
{
	if (isdefined(level.cati_mgci))
		return liste;
	level.cati_mgci = [];
	mg = getentarray("cati_mg", "targetname");
	yer = getentarray("cati_mg_yer", "targetname");
	kalan = [];
	n = 0;
	for (i = 0; i < liste.size; i++)
	{
		g = liste[i];
		if (n < mg.size && (!isdefined(level.price) || g != level.price))
		{
			y = undefined;
			for (k = 0; k < yer.size; k++)
				if (yer[k].script_noteworthy == mg[n].script_noteworthy)
					y = yer[k].origin;
			g thread mg_basinda(mg[n], y);
			level.cati_mgci[n] = g;
			n++;
			continue;
		}
		kalan[kalan.size] = g;
	}
	return kalan;
}

mg_basinda(mg, yer)
{
	self endon("death");
	self.health = 2500;                             // kullanici: MG nisancilari 2500
	self.maxhealth = 2500;
	self notify("yeni_emir");
	self endon("yeni_emir");
	self.goalradius = 12;
	self setgoalpos(yer);
	for (t = 0; t < 60 && distance(self.origin, yer) > 40; t++)
	{
		if (t > 16 && !gorunur(self.origin) && !gorunur(yer))
			self teleport(yer);
		wait 0.5;
	}
	self setgoalpos(yer);
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

siper_al(yer, catida)
{
	self endon("death");
	self notify("yeni_emir");
	self endon("yeni_emir");
	self.siper_yeri = yer;
	self allowedstances("stand", "crouch");
	self.goalradius = 12;
	self.suppressionwait = 0.5;
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
		if ((bekle >= 12 || (catida && t > 30)) && !gorunur(self.origin) && !gorunur(yer))
		{
			self teleport(yer);
			break;
		}
	}
	self setgoalpos(yer);
	self.pathenemyfightdist = 64;                   // pencereden ayrilmaz
	self.pathenemylookahead = 64;
	if (catida)
		return;
	self thread vurulunca_pencere();
	// kullanici: sabit durmasinlar; 30-40 sn'de bir AYNI EVDE baska pencereye
	for (;;)
	{
		wait randomfloatrange(30, 40);
		self yer_degistir();
	}
}

yer_degistir()
{
	yeni = siper_degistir(self.siper_yeri);
	if (!isdefined(yeni))
		return;
	if (isdefined(self.siper_ent))
		self.siper_ent.dolu = undefined;
	yeni.dolu = true;
	self.siper_ent = yeni;
	self.siper_yeri = yeni.origin;
	self.goalradius = 16;
	self setgoalpos(yeni.origin);
}

// "akilli": vurulunca ya da uzun sure hedef goremezse ayni evde baska pencereye
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

// koydeki bos bir siper/pencere noktasi (mevcuttan 200-900 uzakta)
siper_degistir(simdiki)
{
	if (!isdefined(self.oda))
		return undefined;
	aday = ev_noktalari(self.oda);
	if (!aday.size)
		return undefined;
	return aday[randomint(aday.size)];
}

ev_ici_ikikat(p)
{
	if (!isdefined(level.ikikat_yikik))
		return false;
	return (p[0] > -910 && p[0] < -350 && p[1] > 290 && p[1] < 830);
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

grup_dogur(ad)
{
	sp = getentarray(ad, "targetname");
	dogan = [];
	for (i = 0; i < sp.size; i++)
	{
		g = dogur(sp[i]);
		catida = isdefined(sp[i].script_noteworthy) && sp[i].script_noteworthy == "cati";
		sp[i] delete();
		if (!isdefined(g))
			continue;
		dogan[dogan.size] = g;
		if (catida)
		{
			g.goalradius = 16;
			g setgoalpos(g.origin);
		}
		else
			g thread bolge_dolas(g.origin, 350, -9999, 9999);
		wait 0.1;
	}
	if (ad == "koy")
	{
		level.koy_ai = dogan;
		flag_set("koy_dogdu");
	}
	return dogan;
}

// 10'luk dalga: tepelerin arkasindan, once duman; Price yonu soyler
dalga_bas(no)
{
	sp = getentarray("dalga", "targetname");
	yon = [];
	yon[0] = "kuzey";
	yon[1] = "bati";
	yon[2] = "guney";
	y = yon[no % 3];
	sec = [];
	for (i = 0; i < sp.size; i++)
	{
		o = sp[i].origin;
		if ((y == "kuzey" && o[1] > 2500) || (y == "guney" && o[1] < -2500) || (y == "bati" && o[0] < -3500))
			sec[sec.size] = sp[i];
	}
	if (sec.size < 2)
		sec = sp;
	level thread price_der(y);
	if (no >= 1 && no <= 4)
		level thread yari_paletli(no - 1);
	wait 3;
	for (k = 0; k < 10; k++)
	{
		while (getaiarray("axis").size >= 18)
			wait 0.5;
		g = gizli_dogur(sec, 1200);
		if (!isdefined(g))
			continue;
		level.dalga_ai[level.dalga_ai.size] = g;
		g thread saldiran_alman();
		wait 0.3;
	}
}

// kullanici (burya): koye girene kadar durmadan kosar; vurulursa durup carpisir
saldiran_alman()
{
	self endon("death");
	self.pathenemyfightdist = 0;
	self.pathenemylookahead = 0;
	self.ignoresuppression = true;
	self.goalradius = 120;
	self thread vurulunca_dur();
	avlu = getentarray("avlu_siper", "targetname");
	giris = zemin_bul(avlu[randomint(avlu.size)].origin);
	for (t = 0; t < 160 && distance(self.origin, level.koy) > 1050; t++)
	{
		self setgoalpos(giris);
		wait 0.5;
	}
	self notify("koye_girdi");
	self.pathenemyfightdist = 180;                  // kullanici: dikilip durmasin
	self.pathenemylookahead = 180;
	for (;;)
	{
		hedef = level.player;
		ed = distance(self.origin, level.player.origin);
		tum = tum_ingilizler();
		for (i = 0; i < tum.size; i++)
		{
			if (tum[i].origin[2] > 160)
				continue;                       // catidakilere yurunemez
			d = distance(self.origin, tum[i].origin);
			if (d < ed)
			{
				hedef = tum[i];
				ed = d;
			}
		}
		self.goalradius = 96;
		self setgoalpos(zemin_bul(hedef.origin));
		wait randomfloatrange(3, 4.5);
	}
}

vurulunca_dur()
{
	self endon("death");
	self endon("koye_girdi");
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

// YARI PALETLI: yolcular + MG; durunca yolcular iner saldirir, MG ates etmeye devam eder
yari_paletli(k)
{
	arac_yolcu_hazirla(10 + k, "yarim" + (k + 1), 26);
	a = maps\_vehicle::scripted_spawn(10 + k);
	h = a[0];
	yolcu = [];
	if (isdefined(h.riders))
		yolcu = h.riders;
	level thread maps\_vehicle::gopath(h);
	for (i = 0; i < yolcu.size; i++)
		level.dalga_ai[level.dalga_ai.size] = yolcu[i];
	h waittill("reached_end_node");
	wait 4;
	if (isdefined(h.mgturret) && isdefined(h.mgturret[0]))
	{
		h.mgturret[0] setturretteam("axis");
		h.mgturret[0] setmode("auto_nonai");        // nisanci insede de MG susmaz
	}
	for (i = 0; i < yolcu.size; i++)
		if (isalive(yolcu[i]))
			yolcu[i] thread saldiran_alman();
}

// --------------------------------------------------------------------------
// TANKLAR: 4 Panzer II batidan (5 sn arayla, farkli seritler) + 30 Alman
// --------------------------------------------------------------------------
tank_saldirisi()
{
	level.panzerler = [];
	level.tank_piyade = [];
	for (k = 0; k < 4; k++)
	{
		a = maps\_vehicle::scripted_spawn(6 + k);
		p = a[0];
		p thread arac_olumsuz();                // once Crusader'i vuracaklar (kullanici sirasi)
		level.panzerler[k] = p;
		level thread maps\_vehicle::gopath(p);
		p thread durunca_isaretle();
		p thread panzer_ates();
		level thread tank_piyadesi(k, p);
		if (k == 0)
			level thread asker_der("panzer");
		if (k == 2)
			level thread asker_der("tank2");
		wait 5;
	}
}

durunca_isaretle()
{
	self endon("death");
	self waittill("reached_end_node");
	self.durdu = true;
}

tanklar_durdu(sure)
{
	for (t = 0; t < sure * 2; t++)
	{
		n = 0;
		for (k = 0; k < level.panzerler.size; k++)
			if (isdefined(level.panzerler[k].durdu))
				n++;
		if (n >= level.panzerler.size)
			return;
		wait 0.5;
	}
}

// kullanici: Panzer iki katli evin ust katina ates eder; yalniz vurulan (bati) yari yikilir
// ILK ATIS (oyuncu telsizdayken): ust kat bati yarisi animasyonla coker, parcalar duser,
// kaybolur; yerinde ucgen kirik duvar diplari kalir. 1 sn sonra Price ve evdekiler
// telsizli eve kosar; cikar cikmaz IKINCI ATIS: ev ustten asagi coker, harabe kalir
ikikat_yikimi()
{
	hedef = getent("ust_hedef", "targetname");
	p = en_yakin(level.panzerler, hedef.origin);
	p notify("ates_dur");
	p tank_vur(hedef);
	o = hedef.origin;
	patlama(o);
	b = level.ust_bati;
	b notsolid();
	b rotateroll(0 - 9, 2.0, 1.6, 0);               // tek yonlu, hizlanarak (git-gel yok)
	b movez(0 - 170, 2.0, 1.6, 0);
	parca_sac(o + (120, 0, 0), 8);
	playfx(level._effect["bina_toz"], o + (40, 0, -120));
	wait 1.0;
	evdekiler_kacsin();                              // kullanici: 1 sn sonra
	wait 1.0;
	b hide();
	b delete();
	level.ust_yikik moveto(level.ust_yikik.origin + (5120, 0, 0 - 2048), 0.05);
	wait 0.1;
	level.ust_yikik show();
	level.ust_yikik solid();
	maps\_fx::loopfx("tank_duman", o + (80, 0, -40), 0.8);
	// kullanici: Price evden ciktiktan sonra ev vurulur (en fazla 16 sn)
	for (t = 0; t < 32 && (price_evde() || (t < 20 && ikikatta_kimse_var())); t++)
		wait 0.5;
	wait 0.5;
	p tank_vur(hedef);
	o2 = (-630, 560, 250);
	patlama(o2);
	level.ikikat_yikik = true;
	d = level.ust_dogu;
	d notsolid();
	d rotateroll(3, 3.0, 2.4, 0);
	d movez(0 - 340, 3.0, 2.4, 0);                  // kullanici: iyice asagi insin, sonra kaybolsun
	for (k = 0; k < 5; k++)
	{
		playfx(level._effect["bina_toz"], (-630 + randomfloatrange(-200, 200), 560 + randomfloatrange(-200, 200), 120));
		parca_sac(o2, 3);
		wait 0.6;
	}
	d hide();
	d delete();
	level.ust_yikik delete();
	level.harabe moveto(level.harabe.origin + (5120, 0, 0 - 2048), 0.05);
	wait 0.1;
	level.harabe show();
	level.harabe solid();
	badplace_cylinder("harabe", -1, (-630, 560, 40), 330, 400, "axis", "allies");
	playfx(level._effect["bina_toz"], (-630, 560, 80));
	maps\_fx::loopfx("tank_duman", (-630, 560, 120), 0.9);
	maps\_fx::loopfx("tank_ates", (-520, 470, 60), 0.6);
	e = getentarray("pencere", "targetname");
	for (i = 0; i < e.size; i++)
		if (e[i].script_noteworthy == "ikikat")
			e[i].yikik = true;
	p thread panzer_ates();
}

// kullanici: kapali evin tank yonundeki sol (kuzeybati) kosesi vurulur, kose yikilir
kose_vur()
{
	hedef = (450, 680, 120);
	ucak_bombala(hedef);
	patlama(hedef);
	earthquake(0.55, 2, hedef, 2400);
	playfx(level._effect["bina_toz"], (460, 680, 50));
	playfx(level._effect["bina_toz"], (560, 600, 50));
	k = level.kose;
	k notsolid();
	k rotateroll(0 - 7, 1.8, 1.4, 0);               // tek yonlu, hizlanarak
	k movez(0 - 300, 1.8, 1.4, 0);
	parca_sac(hedef, 6);
	wait 0.6;
	parca_sac(hedef + (60, -60, 40), 4);
	wait 1.2;
	k delete();
	level.kose_harabe moveto(level.kose_harabe.origin + (5120, 0, 0 - 2048), 0.05);
	wait 0.1;
	level.kose_harabe show();
	level.kose_harabe solid();
	playfx(level._effect["bina_toz"], (480, 660, 40));
	maps\_fx::loopfx("tank_duman", (450, 690, 70), 0.9);
	maps\_fx::loopfx("tank_ates", (520, 640, 50), 0.6);
}

// kullanici: Panzerlerin dogdugu yerden (kuzeybati vadi) Stuka gelir, tepeden alcalir,
// bombayi birakir, yukselip harita disina gider
ucak_bombala(hedef)
{
	bas = (-6300, 4400, 2600);
	alcak = hedef + vectorScale(vectornormalize((hedef[0] - bas[0], hedef[1] - bas[1], 0)), 0 - 900) + (0, 0, 650);
	cikis = (6400, -3600, 2900);
	u = spawn("script_model", bas);
	u setmodel("xmodel/vehicle_stuka_flying");
	u.angles = vectortoangles(alcak - bas);
	u playsound("plane_flyby_stuka2");
	sure = distance(bas, alcak) / 2600.0;
	u moveto(alcak, sure, 0, sure * 0.3);
	wait sure;
	b = spawn("script_model", u.origin - (0, 0, 40));
	b setmodel("xmodel/prop_stuka_bomb");
	b.angles = u.angles;
	b moveto(hedef, 0.9, 0.5, 0);
	b rotatepitch(40, 0.9);
	u.angles = vectortoangles(cikis - alcak);
	u moveto(cikis, 4.5, 0.8, 0);
	u thread sil_sonra(4.6);
	s = spawn("script_origin", hedef);
	s playsound("mortar_incoming2");
	s thread sil_sonra(4);
	wait 0.9;
	b delete();
}

patlama(o)
{
	playfx(level._effect["tank_patlama"], o);
	playfx(level._effect["duvar_patlama"], o + (60, 0, 0));
	earthquake(0.5, 1.5, o, 1800);
	s = spawn("script_origin", o);
	s playsound("mortar_incoming1");
	wait 0.35;
	playfx(level._effect["tank_patlama"], o);
	s playsound("explo_mine");
	s thread sil_sonra(5);
	radiusDamage(o + (150, 0, 0), 220, 300, 60);
}

// duvar parcalari savrulur, yere duser ve kaybolur (kullanici)
parca_sac(o, adet)
{
	m = [];
	m[0] = "xmodel/egypt_prop_buildingpiece01";
	m[1] = "xmodel/egypt_prop_buildingpiece02";
	m[2] = "xmodel/egypt_prop_buildingpiece03";
	m[3] = "xmodel/egypt_prop_buildingpiece04";
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

price_evde()
{
	if (!isdefined(level.price) || !isalive(level.price))
		return false;
	o = level.price.origin;
	return (o[0] > -910 && o[0] < -350 && o[1] > 290 && o[1] < 830);
}

ikikatta_kimse_var()
{
	tum = tum_ingilizler();
	for (i = 0; i < tum.size; i++)
	{
		o = tum[i].origin;
		if (o[0] > -900 && o[0] < -360 && o[1] > 300 && o[1] < 820)
			return true;
	}
	return false;
}

// Price ve iki katli evdekiler telsizli eve kosar
evdekiler_kacsin()
{
	hedef = [];
	e = getentarray("pencere", "targetname");
	for (i = 0; i < e.size; i++)
		if (e[i].script_noteworthy == "ev")
			hedef[hedef.size] = e[i].origin;
	ic = [];
	ic[0] = zemin_bul((470, -560, 60));
	ic[1] = zemin_bul((800, -560, 60));
	ic[2] = zemin_bul((560, -700, 60));
	ic[3] = zemin_bul((760, -700, 60));
	tum = tum_ingilizler();
	n = 0;
	for (i = 0; i < tum.size; i++)
	{
		g = tum[i];
		o = g.origin;
		evde = (o[0] > -910 && o[0] < -350 && o[1] > 290 && o[1] < 830);
		if (!evde && (!isdefined(level.price) || g != level.price))
			continue;
		if (n < hedef.size)
			y = hedef[n];
		else
			y = ic[(n - hedef.size) % ic.size];
		n++;
		g.oda = "ev";
		g thread kacarak_siper(y);
	}
}

kacarak_siper(yer)
{
	self endon("death");
	self notify("yeni_emir");
	self endon("yeni_emir");
	self.ignoresuppression = true;
	self.pathenemyfightdist = 0;
	self.goalradius = 24;
	self setgoalpos(yer);
	self hedef_bekle(20);
	self.pathenemyfightdist = 400;
	self.ignoresuppression = false;
	self thread siper_al(yer, false);
}

// telsiz: sari yanip soner, F ile kullanilir
telsiz_kullan()
{
	r = getent("telsiz", "targetname");
	t = getent("telsiz_tetik", "targetname");
	t.origin = t.eski;
	t sethintstring(&"KUMTEPE_PLATFORM_TELSIZ");
	t waittill("trigger");
	r notify("kullanildi");
	r setmodel("xmodel/military_german_fieldradio_green");
	t delete();
	ses_cal(level.player, "kumtepe_asker_telsiz", 10);     // King-Bes, Dog-Alti... zirhli destek
	ses_cal(r, "kumtepe_asker_cevap", 9);                  // (radyo) Anlasildi
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

ingiliz_takviyesi_gecikmeli(sure)
{
	wait sure;
	ingiliz_takviyesi();
}

// Panzer koye ates eder (stok duhoc_defend kalibi); ara sira oyuncunun yakinina
panzer_ates()
{
	self endon("death");
	self endon("ates_dur");
	hedef = getentarray("tank_hedef", "targetname");
	wait randomfloatrange(1, 2.5);                  // kullanici: gec ates ediyorlardi
	for (;;)
	{
		if (randomint(4) == 0)
		{
			t = spawn("script_origin", level.player.origin + (randomfloatrange(-260, 260), randomfloatrange(-260, 260), 30));
			self tank_vur(t);
			t delete();
		}
		else
			self tank_vur(hedef[randomint(hedef.size)]);
		wait randomfloatrange(5, 8);
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

tank_piyadesi(k, tank)
{
	sp = [];
	tum = getentarray("tank_piyade", "targetname");
	for (i = 0; i < tum.size; i++)
		if (tum[i].script_noteworthy == "" + (k + 1))
			sp[sp.size] = tum[i];
	adet = 7 + (k < 2);                         // 8 + 8 + 7 + 7 = 30
	for (i = 0; i < adet && i < sp.size; i++)
	{
		g = dogur(sp[i]);
		if (!isdefined(g))
			continue;
		level.tank_piyade[level.tank_piyade.size] = g;
		g thread tankin_arkasinda(tank, i);
		wait 0.2;
	}
}

// tankin arkasinda yuruyerek gelir; tank durunca koye saldirir
tankin_arkasinda(tank, i)
{
	self endon("death");
	self.goalradius = 64;
	yan = ((i % 3) - 1) * 90;
	while (isdefined(tank) && !isdefined(tank.durdu))
	{
		ileri = anglestoforward(tank.angles);
		sag = anglestoright(tank.angles);
		p = tank.origin - vectorScale(ileri, 220 + (i / 3) * 70) + vectorScale(sag, yan);
		self setgoalpos(zemin_bul(p));
		wait 1;
	}
	self thread saldiran_alman();                   // kullanici: tank durdugu anda koye saldiri
}

// --------------------------------------------------------------------------
// KURTULUS: 4 Crusader (gelinen yoldan, gorunmeden); biri 1 can -> Panzer vurur;
// sonra Crusaderlar Panzerleri patlatir
// --------------------------------------------------------------------------
crusader_gelir()
{
	level.crusaderlar = [];
	for (k = 0; k < 4; k++)
	{
		a = maps\_vehicle::scripted_spawn(2 + k);
		c = a[0];
		level.crusaderlar[k] = c;
		if (k > 0)
			c thread arac_olumsuz();            // kullanici: Crusaderlar olumsuz, biri haric (1 can)
		level thread crusader_yola(c, k * 2.6);  // kullanici: ic ice gelmesinler
		c thread durunca_isaretle();
		wait 1.25;                              // kullanici: 1.25 sn arayla
	}
	iprintlnbold(&"KUMTEPE_MSG_CRUSADER");
	level thread asker_der("zebra");
	price_der("crusader");
	// kurban koyun icine varinca bir Panzer onu vurur
	kurban = level.crusaderlar[0];
	for (t = 0; t < 80 && isdefined(kurban) && !isdefined(kurban.durdu); t++)
		wait 0.5;
	atan = undefined;
	if (isdefined(kurban))
		atan = en_yakin(level.panzerler, kurban.origin);
	if (isdefined(atan) && isdefined(kurban))
	{
		atan notify("ates_dur");
		atan tank_vur(kurban);
		atan thread panzer_ates();
	}
	wait 0.3;
	if (isdefined(kurban))
	{
		kurban.health = 1;
		kurban dodamage(5000, kurban.origin);
		kurban notify("death");
	}
	level thread asker_der("zebra_vuruldu");
	// digerleri yerine varsin; Panzerlerle carpissinlar
	for (t = 0; t < 70; t++)
	{
		n = 0;
		for (k = 1; k < 4; k++)
			if (isdefined(level.crusaderlar[k].durdu))
				n++;
		if (n >= 3)
			break;
		wait 0.5;
	}
	for (i = 0; i < level.panzerler.size; i++)
		level.panzerler[i] thread panzer_crusadera();
	wait 1.5;
	for (i = 0; i < level.panzerler.size; i++)
	{
		p = level.panzerler[i];
		if (!isdefined(p))
			continue;
		c = level.crusaderlar[1 + (i % 3)];
		if (isdefined(c))
			c tank_vur(p);                      // kullanici: tek atista patlar
		wait 0.3;
		p notify("ates_dur");
		p notify("olumsuz_bitti");
		p.health = 1;
		p dodamage(50000, p.origin);
		p notify("death");
		wait randomfloatrange(2, 3.5);
	}
	level thread asker_der("tamam");
}

crusader_yola(c, gecikme)
{
	wait gecikme;
	if (isdefined(c))
		maps\_vehicle::gopath(c);
}

// Panzer Crusaderlara karsilik verir (Crusaderlar olumsuz)
panzer_crusadera()
{
	self endon("death");
	self notify("ates_dur");
	self endon("ates_dur");
	for (;;)
	{
		c = en_yakin(level.crusaderlar, self.origin);
		if (isdefined(c))
			self tank_vur(c);
		wait randomfloatrange(3, 5);
	}
}

en_yakin(liste, nokta)
{
	en = undefined;
	for (i = 0; i < liste.size; i++)
		if (isdefined(liste[i]) && (!isdefined(en) || distance(liste[i].origin, nokta) < distance(en.origin, nokta)))
			en = liste[i];
	return en;
}

// 20 Ingiliz yaya gelir, koyde siper alir
ingiliz_takviyesi()
{
	sp = getentarray("ingiliz", "targetname");
	yeni = [];
	for (i = 0; i < sp.size; i++)
	{
		g = dogur(sp[i]);
		sp[i] delete();
		if (!isdefined(g))
			continue;
		g.health = 1450;
		g.maxhealth = 1450;
		yeni[yeni.size] = g;
		level.ingilizler[level.ingilizler.size] = g;
		wait 0.15;
	}
	test_yaz("ingiliz takviyesi: " + yeni.size);
	// kullanici: tek binada toplanmasinlar -> koyun her yerine (siper dugumleri)
	yer = [];
	for (i = 0; i < level.siper.size; i++)
		if (distance(level.siper[i].origin, level.koy) < 1150)
			yer[yer.size] = level.siper[i];
	yer = karistir(yer);
	for (i = 0; i < yeni.size; i++)
	{
		if (!yer.size)
			break;
		yeni[i] thread avluda_siper(yer[i % yer.size]);
	}
}

avluda_siper(dugum)
{
	self endon("death");
	self notify("yeni_emir");
	self endon("yeni_emir");
	self.goalradius = 32;
	self setgoalnode(dugum);
	for (;;)
	{
		wait randomfloatrange(30, 45);              // ara sira yakindaki baska sipere
		s = siper_bul(self.origin + (randomfloatrange(-500, 500), randomfloatrange(-500, 500), 0), 400);
		if (isdefined(s) && distance(s.origin, level.koy) < 1150)
			self setgoalnode(s);
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
		yakin = distance(self.origin, p) < 550;
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
		if (yakin)
			wait randomfloatrange(2, 4);
		else
			wait randomfloatrange(7, 14);
	}
}

// --------------------------------------------------------------------------
// EKIP BEYNI (metel/burya): takip / hucum / bekle
// --------------------------------------------------------------------------
ekip_beyni()
{
	for (;;)
	{
		wait 1;
		if (!flag("indik"))
			continue;
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
		g.pathenemyfightdist = 600;
		g.pathenemylookahead = 600;
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

// takilan ekip uyesi: 9 sn kipirdamaz ve oyuncudan uzaksa gorulmeden arkaya alinir
takili_kurtar()
{
	self endon("death");
	son = self.origin;
	takili = 0;
	while (level.asama == "ASSAULT_VILLAGE" || level.asama == "CONVOY")
	{
		wait 3;
		if (distance(self.origin, son) > 40 || distance(self.origin, level.player.origin) < 700)
		{
			son = self.origin;
			takili = 0;
			continue;
		}
		takili++;
		if (takili >= 3)
		{
			ileri = anglestoforward(level.player getplayerangles());
			p = zemin_bul(level.player.origin - vectorScale((ileri[0], ileri[1], 0), 300) + (randomfloatrange(-120, 120), randomfloatrange(-120, 120), 0));
			if (!gorunur(self.origin) && !gorunur(p))
			{
				self teleport(p);
				takili = 0;
			}
		}
		son = self.origin;
	}
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
	perde fadeOverTime(7);
	perde.alpha = 1;
	wait 7.5;
	test_yaz("GOREV TAMAM");
	missionSuccess("credits", false);
}

// --------------------------------------------------------------------------
// SES / MUZIK: her replik kendi script_origin'inden (burya olcusu)
// --------------------------------------------------------------------------
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
		ses_cal(g, "kumtepe_price_" + replik, 11);
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
	org waittill_any_timeout_kum(sure, "ses_bitti", "yok");
	org delete();
}

waittill_any_timeout_kum(sure, a, b)
{
	self endon(a);
	self endon(b);
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
	ses_cal(konusan, "kumtepe_asker_" + ad, 6);
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
// OYUNCU SINIRI: gercek gorunmez duvar + kacaklar icin 1 sn sonra geri alma
// --------------------------------------------------------------------------
sinir_bekcisi()
{
	son = level.player.origin;
	disari = 0;
	for (;;)
	{
		p = level.player.origin;
		if (cokgen_icinde(p, level.koy_kare))
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
		level.player.health = 1000;
		wait 0.5;
	}
}

// --------------------------------------------------------------------------
// EKRAN TURU (kr_tur 1): gorsel kalite kontrolu (skill visual-qa)
// --------------------------------------------------------------------------
ekran_turu()
{
	level.player takeallweapons();
	level thread test_olumsuz();
	n = [];
	a = [];
	n[n.size] = (0, 0, 3200);         a[a.size] = (89, 90, 0);    // 1 koy ustten
	n[n.size] = (1500, -1000, 5200);  a[a.size] = (70, 135, 0);   // 2 dogu yolu kus bakisi
	n[n.size] = (6000, -4200, 900);   a[a.size] = (25, 140, 0);   // 3 konvoy vadisi (harita disi)
	n[n.size] = (5400, -1700, 280);   a[a.size] = (6, 160, 0);    // 4 yol sinirdan iceri
	n[n.size] = (3300, -650, 230);    a[a.size] = (5, 160, 0);    // 5 yol orta
	n[n.size] = (2000, 100, 200);     a[a.size] = (5, 140, 0);    // 6 koye yaklasma
	n[n.size] = (1250, 800, 160);     a[a.size] = (4, 150, 0);    // 7 durak oncesi
	n[n.size] = (782, 1071, 140);     a[a.size] = (6, 225, 0);    // 8 KAMYON DURAGI -> koy
	n[n.size] = (500, 1500, 300);     a[a.size] = (25, 300, 0);   // 9 durak ustten
	n[n.size] = (4000, -2600, 300);   a[a.size] = (4, 330, 0);    // 10 yol geriye bakis (bas gorunuyor mu)
	n[n.size] = (-200, -200, 120);    a[a.size] = (4, 45, 0);     // 11 avlu, kuyu
	n[n.size] = (250, 250, 120);      a[a.size] = (4, 225, 0);    // 12 avlu siperleri
	n[n.size] = (-630, 120, 140);     a[a.size] = (6, 90, 0);     // 13 iki katli on
	n[n.size] = (-1250, 560, 300);    a[a.size] = (8, 0, 0);      // 14 iki katli bati (vurulacak yari)
	n[n.size] = (-630, 500, 110);     a[a.size] = (4, 0, 0);      // 15 iki katli ic
	n[n.size] = (620, -560, 110);     a[a.size] = (6, 0, 0);      // 16 ev ic + telsiz
	n[n.size] = (-180, -560, 130);    a[a.size] = (4, 180, 0);    // 17 merdiven
	n[n.size] = (-600, -560, 270);    a[a.size] = (20, 0, 0);     // 18 cati
	n[n.size] = (-4500, 3500, 1400);  a[a.size] = (40, 300, 0);   // 19 Panzer vadisi kus bakisi
	n[n.size] = (-5300, 700, 400);    a[a.size] = (5, 70, 0);     // 20 Panzer vadisi ici
	n[n.size] = (-1100, 0, 220);      a[a.size] = (4, 180, 0);    // 21 bati: Panzer duraklari
	n[n.size] = (-1600, 1600, 600);   a[a.size] = (25, 0, 0);     // 22 Crusader kuzey rotasi
	n[n.size] = (-1600, -1600, 600);  a[a.size] = (25, 0, 0);     // 23 Crusader guney rotasi
	n[n.size] = (200, 2600, 400);     a[a.size] = (10, 90, 0);    // 24 kuzey yari paletli/dalga
	n[n.size] = (300, -2600, 400);    a[a.size] = (10, 270, 0);   // 25 guney yari paletli/dalga
	n[n.size] = (0, 1500, 180);       a[a.size] = (4, 90, 0);     // 26 koy sinirindan kuzeye
	n[n.size] = (1500, 0, 180);       a[a.size] = (4, 0, 0);      // 27 koy sinirindan doguya
	n[n.size] = (-1500, -1500, 180);  a[a.size] = (4, 225, 0);    // 28 koy sinirindan GB
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

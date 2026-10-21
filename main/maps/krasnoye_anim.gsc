// krasnoye_anim.gsc -- tankhunt_anim.gsc kalibi.
// Leonov replikleri: level.scrsound["leonov"][ad] = alias. Ses: stok CoD2
// Sovyet seslendirmesi (Tegmen Volsky), bkz. krasnoye_tools/ses_kur.py. anim_single_solo
// animasyonsuz replikte sesi SaySpecificDialogue ile calar, dudak hareketi
// (anim_facialFiller) ekler; altyazi alias'in subtitle sutunundan gelir.
#include maps\_anim;
#using_animtree("generic_human");

main()
{
	// ---- Leonov (ses: soundaliases/krasnoye.csv) ----
	ad = [];
	ad[ad.size] = "giris";
	ad[ad.size] = "ilerle";
	ad[ad.size] = "evler";
	ad[ad.size] = "koy_temiz";
	ad[ad.size] = "savunma";
	ad[ad.size] = "kamyon";
	ad[ad.size] = "yaripalet";
	ad[ad.size] = "tank";
	ad[ad.size] = "bomba_al";
	ad[ad.size] = "bomba_yapistir";
	ad[ad.size] = "geri_cekiliyor";
	ad[ad.size] = "zafer";
	for (i = 0; i < ad.size; i++)
		level.scrsound["leonov"][ad[i]] = "krasnoye_leonov_" + ad[i];
	level.scrsound["leonov"]["bekle"] = "demolition_rs1_countingonus";   // demolition komiser
	// takviye haberini Leonov degil, en yakin asker verir (farkli ses)
	level.scrsound["generic"]["takviye"] = "krasnoye_asker_takviye";

	// ---- tank yanasma sahnesi (tankhunt_anim.gsc birebir) ----
	level.scr_anim["gunguy"]["grenadetank"]				= (%panzertank2_runup_gunguy);
	level.scr_anim["gunguy"]["grenadetank_run"]			= (%panzertank2_hatchopencloseandrun_gunguy);
	level.scr_anim["runupguy"]["grenadetank"]			= (%panzertank2_runup_grenadeguy);
	level.scr_anim["runupguy"]["grenadetank_loop"][0]	= (%panzertank2_waitloop_grenadeguy);
	level.scr_anim["runupguy"]["grenadetank_run"]		= (%panzertank2_hatchopencloserun_grenadeguy);

	level.scrsound["runupguy"]["demolition_rs4_motherrussia"]	= "demolition_rs4_motherrussia";
	level.scrsound["runupguy"]["commissar_charge_killfascists"]	= "commissar_charge_killfascists";
	level.scrsound["runupguy"]["commissar_charge_attack"]		= "commissar_charge_attack";
	level.scrsound["runupguy"]["moscow_rs3_fireinthehole"]		= "moscow_rs3_fireinthehole";

	addNotetrack_customFunction("gunguy", "fire = open_hatch", ::shootGun, "grenadetank_run");
	addNotetrack_sound("runupguy", "weap_fraggrenade_pin", "grenadetank_run", "weap_fraggrenade_pin");
	addNotetrack_sound("runupguy", "weap_fraggrenade_fire", "grenadetank_run", "weap_fraggrenade_fire");
	addNotetrack_sound("runupguy", "open_hatch", "grenadetank_run", "tank_hatch");
}

shootGun(guy)
{
	guy shoot();
	wait .15;
	if (guy.weapon != "mosin_nagant")
		guy shoot();
	wait .2;
	if (guy.weapon != "mosin_nagant")
		guy shoot();
	wait .3;
	if (guy.weapon != "mosin_nagant")
		guy shoot();
	wait .2;
	guy shoot();
}

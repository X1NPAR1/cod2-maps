// kasrelbab_anim.gsc -- replik tablosu (stok Price sesleri, bkz. kasrelbab_tools/ses_kur.py)
#include maps\_anim;
#using_animtree("generic_human");

main()
{
	ad = [];
	ad[ad.size] = "gizlen";	ad[ad.size] = "brifing";	ad[ad.size] = "hucum";	ad[ad.size] = "git";
	ad[ad.size] = "flak";	ad[ad.size] = "flak_bitti";	ad[ad.size] = "tank";	ad[ad.size] = "toplan";
	ad[ad.size] = "kamyon";	ad[ad.size] = "final";
	for (i = 0; i < ad.size; i++)
		level.scrsound["price"][ad[i]] = "kasrelbab_price_" + ad[i];
	// final: stok beltot McGregor sahnesi (kamyonu kontrol et + surucu koltuguna bin)
	level.scr_anim["price"]["truckscene"] = (%beltot_truckscene_checktruck_guy);
	level.scr_anim["price"]["drive_loop"][0] = (%germantruck_driver_sitidle_loop);
	// final: iki asker stok buddyjump ile kasaya (tag_climbnode), sonra ayakta bekler
	level.kr_anim = [];
	level.kr_anim["kasa_tirman"] = [];
	level.kr_anim["kasa_tirman"][0] = %germantruck_guyA_climbin;
	level.kr_anim["kasa_tirman"][1] = %germantruck_guyB_climbin;
	level.kr_anim["kasa_bekle"] = %stand_alert_1;
}

// beltot anim_truck_door: kamyonun kapisi Price'in kontrol sahnesiyle birlikte acilip kapanir
#using_animtree("germantruck");
kamyon_kapi_sahnesi()
{
	self endon("death");
	self useanimtree(#animtree);
	self setanim(%beltot_truckscene_checktruck_truck);
	wait 6.3;
	self playsound("truck_door_open");
	wait 10.1;
	self playsound("car_door_close");
}

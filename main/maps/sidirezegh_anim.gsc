// sidirezegh_anim.gsc -- replik tablosu (stok Price sesleri, bkz. sidirezegh_tools/ses_kur.py)
#include maps\_anim;
#using_animtree("generic_human");

main()
{
	ad = [];
	ad[ad.size] = "giris";	ad[ad.size] = "savun";	ad[ad.size] = "kuzey";	ad[ad.size] = "guney";
	ad[ad.size] = "dogu";	ad[ad.size] = "hucum";	ad[ad.size] = "final1";	ad[ad.size] = "final2";
	ad[ad.size] = "kamyon";
	for (i = 0; i < ad.size; i++)
		level.scrsound["price"][ad[i]] = "sidirezegh_price_" + ad[i];
	// final: Price kapiyi tekmeler (stok beltot/breakout: "kick" notetrack)
	level.scr_anim["price"]["tekme"] = (%chateau_kickdoor1);
	// final: stok beltot McGregor sahnesi (kamyonu kontrol et + surucu koltuguna bin)
	level.scr_anim["price"]["truckscene"] = (%beltot_truckscene_checktruck_guy);
	level.scr_anim["price"]["drive_loop"][0] = (%germantruck_driver_sitidle_loop);
	// final: Ingilizler stok buddyjump ile kasaya (tag_climbnode), sonra ayakta bekler
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

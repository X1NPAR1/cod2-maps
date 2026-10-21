// metel_anim.gsc -- krasnoye_anim kalibi.
// Leonov replikleri: level.scrsound["leonov"][ad] = "metel_leonov_<ad>".
// Ses: stok Tegmen Volsky (Turkce altyazili), bkz. metel_tools/ses_kur.py.
#include maps\_anim;
#using_animtree("generic_human");

main()
{
	ad = [];
	ad[ad.size] = "giris";
	ad[ad.size] = "hucum";
	ad[ad.size] = "havan1";
	ad[ad.size] = "havan2";
	ad[ad.size] = "karakol";
	ad[ad.size] = "kapi";
	ad[ad.size] = "ust_temiz";
	ad[ad.size] = "savunma";
	ad[ad.size] = "saldiri";
	ad[ad.size] = "kacis";
	ad[ad.size] = "final1";
	ad[ad.size] = "final2";
	for (i = 0; i < ad.size; i++)
		level.scrsound["leonov"][ad[i]] = "metel_leonov_" + ad[i];
	// takviye haberini Leonov degil, bir asker verir
	level.scrsound["generic"]["takviye"] = "metel_asker_takviye";
}

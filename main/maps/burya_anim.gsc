// burya_anim.gsc -- replik tablosu (stok Volsky + Demolition sesleri, bkz. burya_tools/ses_kur.py)
#include maps\_anim;
#using_animtree("generic_human");

main()
{
	ad = [];
	ad[ad.size] = "giris";	ad[ad.size] = "pusu";	ad[ad.size] = "ilerle";	ad[ad.size] = "kamp";
	ad[ad.size] = "mg";	ad[ad.size] = "savun";	ad[ad.size] = "saldiri";	ad[ad.size] = "temizle";
	ad[ad.size] = "kamp_bizde";	ad[ad.size] = "bomba";	ad[ad.size] = "iyi_is";
	ad[ad.size] = "final1";	ad[ad.size] = "final2";
	for (i = 0; i < ad.size; i++)
		level.scrsound["leonov"][ad[i]] = "burya_leonov_" + ad[i];
}

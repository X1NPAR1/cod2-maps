// kumtepe_anim.gsc -- replik tablosu (stok Price sesleri, bkz. kumtepe_tools/ses_kur.py)
#include maps\_anim;
#using_animtree("generic_human");

main()
{
	ad = [];
	ad[ad.size] = "giris";	ad[ad.size] = "inis";	ad[ad.size] = "hucum";	ad[ad.size] = "savun";
	ad[ad.size] = "kuzey";	ad[ad.size] = "guney";	ad[ad.size] = "bati";	ad[ad.size] = "dogu";
	ad[ad.size] = "tank";	ad[ad.size] = "crusader";	ad[ad.size] = "final1";	ad[ad.size] = "final2";
	for (i = 0; i < ad.size; i++)
		level.scrsound["price"][ad[i]] = "kumtepe_price_" + ad[i];
}

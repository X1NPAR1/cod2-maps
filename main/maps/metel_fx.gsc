// metel_fx.gsc -- krasnoye_fx (tankhunt_fx) kalibi + havan efektleri.
// Efekt dosyalari iwd'den dogrulandi: large_snow_explode1, mortar_flash.
main()
{
	precacheFX();
	level thread karYagisi();
	dunyaFX();
}

precacheFX()
{
	adim = [];
	adim[adim.size] = "snow";	adim[adim.size] = "gravel";	adim[adim.size] = "mud";
	adim[adim.size] = "grass";	adim[adim.size] = "dirt";	adim[adim.size] = "concrete";
	adim[adim.size] = "rock";	adim[adim.size] = "asphalt";	adim[adim.size] = "plaster";
	adim[adim.size] = "wood";
	for (i = 0; i < adim.size; i++)
		animscripts\utility::setFootstepEffect(adim[i], loadfx("fx/impacts/footstep_snow.efx"));

	level._effect["snow_light"]	= loadfx("fx/misc/snow_light.efx");
	level._effect["snow_wind"]	= loadfx("fx/misc/snow_wind_cityhall.efx");
	level._effect["cold_breath"] = loadfx("fx/misc/cold_breath.efx");   // setEnvironment("cold") ister (olculdu)
	// havan barajlari (maps\_mortar::generic_style, bergstein_fx kalibi)
	level._effect["havan_b"]	= loadfx("fx/explosions/large_snow_explode1.efx");
	level._effect["havan_c"]	= loadfx("fx/explosions/large_snow_explode1.efx");
	level._effectType["havan_b"] = "mortar";
	level._effectType["havan_c"] = "mortar";
	level._effect["havan_namlu"] = loadfx("fx/muzzleflashes/mortar_flash.efx");
	level._effect["kapi_toz"]   = loadfx("fx/dust/dust_door_ambush.efx");
	level._effect["kapi_kiymik"] = loadfx("fx/impacts/large_woodhit.efx");
}

// tankhunt playerEffect(): oyuncunun ustunde hafif kar (gorusu kapatmaz)
karYagisi()
{
	player = getent("player", "classname");
	for (;;)
	{
		playfx(level._effect["snow_light"], player.origin + (0, 0, 300), player.origin + (0, 0, 350));
		wait (0.75);
	}
}

// yerde savrulan kar: yollar, avlu, kopru basi, mevzi tepeleri
dunyaFX()
{
	p = [];
	p[p.size] = (120, -1900, 0);	p[p.size] = (0, -800, 0);	p[p.size] = (-1000, -650, 0);
	p[p.size] = (-1750, 300, 0);	p[p.size] = (-150, -250, 0);	p[p.size] = (-150, 1150, 0);
	p[p.size] = (1000, -650, 0);	p[p.size] = (1500, 1050, 0);	p[p.size] = (-2300, 1400, 210);
	p[p.size] = (2700, 1100, 240);	p[p.size] = (2200, 0, 0);
	for (i = 0; i < p.size; i++)
		maps\_fx::loopfx("snow_wind", p[i], 1, p[i] + (0, 0, 100));
}

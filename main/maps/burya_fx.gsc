// burya_fx.gsc -- efekt tablosu (her dosya iw_07.iwd'de dogrulandi).
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
	level._effect["cold_breath"]	= loadfx("fx/misc/cold_breath.efx");   // setEnvironment("cold") ister
	// konvoy pususu: mayin patlamasi + yanan kamyon
	level._effect["mayin"]		= loadfx("fx/explosions/large_snow_explode1.efx");
	level._effect["kamyon_ates"]	= loadfx("fx/fire/halftrack_fire.efx");
	level._effect["kamyon_duman"]	= loadfx("fx/smoke/damaged_vehicle_smoke.efx");
	// merkez bina yikimi (stok demolition_fx kalibi)
	level._effect["bina_taban"]	= loadfx("fx/explosions/default_explosion.efx");
	level._effect["bina_pencere"]	= loadfx("fx/explosions/demolition_windowBlast.efx");
	level._effect["bina_toz"]	= loadfx("fx/dust/demolition_dust_base.efx");
	level._effect["bina_sutun"]	= loadfx("fx/dust/demolition_dust_column.efx");
	level._effect["bina_toz_son"]	= loadfx("fx/dust/demolition_dust_base_after.efx");
	level._effect["bina_ates"]	= loadfx("fx/fire/building_fire_med.efx");
	level._effect["bina_duman"]	= loadfx("fx/smoke/thin_black_smoke_M.efx");
	level._effect["bina_buyuk"]	= loadfx("fx/explosions/ammo_supply_exp.efx");
	// kule devrilmesi: tahta kiriklari ve toz
	level._effect["duman_bombasi"]	= loadfx("fx/props/german_smoke_grenade.efx");
	level._effect["kule_tahta"]	= loadfx("fx/explosions/grenadeExp_wood.efx");
	level._effect["kule_kirik"]	= loadfx("fx/impacts/large_woodhit.efx");
	level._effect["kule_toz"]	= loadfx("fx/dust/toujane_tunnel_collapse.efx");
}

karYagisi()
{
	player = getent("player", "classname");
	for (;;)
	{
		playfx(level._effect["snow_light"], player.origin + (0, 0, 300), player.origin + (0, 0, 350));
		wait (0.75);
	}
}

dunyaFX()
{
	p = [];
	p[p.size] = (-3200, -2600, 60);	p[p.size] = (-1600, -1400, 60);	p[p.size] = (0, -500, 60);
	p[p.size] = (1500, 600, 60);	p[p.size] = (2300, 1200, 60);	p[p.size] = (3000, 1800, 60);
	p[p.size] = (2200, 2400, 60);	p[p.size] = (3800, 2900, 60);
	for (i = 0; i < p.size; i++)
		maps\_fx::loopfx("snow_wind", p[i], 1, p[i] + (0, 0, 100));
}

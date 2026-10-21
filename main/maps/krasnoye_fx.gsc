// krasnoye_fx.gsc -- tankhunt_fx.gsc kalibi birebir (kar yagisi, savrulan kar,
// kar ayak izleri). Efekt adlari stok iwd'den.
main()
{
	precacheFX();
	level thread karYagisi();
	dunyaFX();
}

precacheFX()
{
	animscripts\utility::setFootstepEffect ("snow",		loadfx ("fx/impacts/footstep_snow.efx"));
	animscripts\utility::setFootstepEffect ("gravel",	loadfx ("fx/impacts/footstep_snow.efx"));
	animscripts\utility::setFootstepEffect ("mud",		loadfx ("fx/impacts/footstep_snow.efx"));
	animscripts\utility::setFootstepEffect ("grass",	loadfx ("fx/impacts/footstep_snow.efx"));
	animscripts\utility::setFootstepEffect ("dirt",		loadfx ("fx/impacts/footstep_snow.efx"));
	animscripts\utility::setFootstepEffect ("concrete",	loadfx ("fx/impacts/footstep_snow.efx"));
	animscripts\utility::setFootstepEffect ("rock",		loadfx ("fx/impacts/footstep_snow.efx"));
	animscripts\utility::setFootstepEffect ("asphalt",	loadfx ("fx/impacts/footstep_snow.efx"));
	animscripts\utility::setFootstepEffect ("plaster",	loadfx ("fx/impacts/footstep_snow.efx"));
	animscripts\utility::setFootstepEffect ("wood",		loadfx ("fx/impacts/footstep_snow.efx"));

	level._effect["snow_light"]			= loadfx ("fx/misc/snow_light.efx");
	level._effect["snow_wind"]			= loadfx ("fx/misc/snow_wind_cityhall.efx");
	level._effect["cold_breath"]		= loadfx ("fx/misc/cold_breath.efx");
	level._effect["sticky_explosion"]	= loadfx ("fx/explosions/default_explosion.efx");
	level._effect["sticky_explosion_smoke"] = loadfx ("fx/smoke/thin_black_smoke_S.efx");
	level._effect["heavysmoke"]			= loadfx ("fx/smoke/damaged_vehicle_smoke.efx");
}

// tankhunt playerEffect(): oyuncunun ustunde surekli hafif kar
karYagisi()
{
	player = getent("player", "classname");
	for (;;)
	{
		playfx(level._effect["snow_light"], player.origin + (0, 0, 300), player.origin + (0, 0, 350));
		wait (0.75);
	}
}

// yerde savrulan kar (koy meydani, tarla, savunma hatti)
dunyaFX()
{
	p = [];
	p[p.size] = (0, 200, 0);       p[p.size] = (-900, 300, 0);   p[p.size] = (900, 100, 0);
	p[p.size] = (-400, -1000, 0);  p[p.size] = (500, -1300, 0);  p[p.size] = (-1500, -1700, 0);
	p[p.size] = (1200, -2000, 0);  p[p.size] = (0, 1600, 0);     p[p.size] = (-1300, 1300, 0);
	for (i = 0; i < p.size; i++)
		maps\_fx::loopfx("snow_wind", p[i], 1, p[i] + (0, 0, 100));
}

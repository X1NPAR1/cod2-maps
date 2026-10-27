// sidirezegh_fx.gsc -- efekt tablosu (her dosya iw_*.iwd'de dogrulandi).
main()
{
	precacheFX();
	dunyaFX();
}

precacheFX()
{
	level._effect["kum_ruzgar"]	= loadfx("fx/dust/dust_wind_elalamein.efx");
	level._effect["kum_ruzgar_alcak"]	= loadfx("fx/dust/dust_wind_elalamein_low.efx");
	level._effect["duman_bombasi"]	= loadfx("fx/props/german_smoke_grenade.efx");
	level._effect["tank_patlama"]	= loadfx("fx/explosions/panzer_explosion.efx");
	level._effect["tank_ates"]	= loadfx("fx/fire/tank_fire_engine.efx");
	level._effect["tank_duman"]	= loadfx("fx/smoke/damaged_vehicle_smoke.efx");
	level._effect["duvar_patlama"]	= loadfx("fx/explosions/demolition_windowBlast.efx");
	level._effect["bina_toz"]	= loadfx("fx/dust/demolition_dust_base.efx");
	level._effect["kum_mermi"]	= loadfx("fx/impacts/20mil_dirthit_libya.efx");
	level._effect["uzak_patlama"]	= loadfx("fx/explosions/default_explosion.efx");
}

// avlu ve col boyunca ruzgarla savrulan kum
dunyaFX()
{
	p = [];
	p[p.size] = (0, 0, 60);		p[p.size] = (-1500, 1200, 80);	p[p.size] = (1500, -1300, 80);
	p[p.size] = (-2600, -600, 80);	p[p.size] = (2600, 900, 80);	p[p.size] = (300, 2600, 120);
	p[p.size] = (-300, -2600, 120);	p[p.size] = (-3800, 1800, 120);	p[p.size] = (3600, -1800, 120);
	for (i = 0; i < p.size; i++)
		maps\_fx::loopfx("kum_ruzgar", p[i], 1.4, p[i] + (0, 0, 100));
	maps\_fx::loopfx("kum_ruzgar_alcak", (-400, 400, 50), 1.2, (-400, 400, 150));
	maps\_fx::loopfx("kum_ruzgar_alcak", (400, -400, 50), 1.2, (400, -400, 150));
}

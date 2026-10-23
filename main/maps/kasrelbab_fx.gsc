// kasrelbab_fx.gsc -- efekt tablosu (her dosya iw_*.iwd'de dogrulandi).
main()
{
	level._effect["kum_ruzgar"]	= loadfx("fx/dust/dust_wind_eldaba.efx");
	level._effect["kum_alcak"]	= loadfx("fx/dust/dust_wind_elalamein_low.efx");
	level._effect["tank_patlama"]	= loadfx("fx/explosions/panzer_explosion.efx");
	level._effect["tank_ates"]	= loadfx("fx/fire/tank_fire_engine.efx");
	level._effect["tank_duman"]	= loadfx("fx/smoke/damaged_vehicle_smoke.efx");
	level._effect["duvar_patlama"]	= loadfx("fx/explosions/demolition_windowBlast.efx");
	level._effect["bina_toz"]	= loadfx("fx/dust/demolition_dust_base.efx");
	level._effect["flak_alev"]	= loadfx("fx/muzzleflashes/flak_flash.efx");
	level._effect["flak_puf"]	= loadfx("fx/explosions/flak_puff.efx");
	level._effect["flak_patlama"]	= loadfx("fx/explosions/flak88_explosion.efx");
	level._effect["flak_toz"]	= loadfx("fx/dust/flak_dust_blowback.efx");
	level._effect["duman_bombasi"]	= loadfx("fx/props/german_smoke_grenade.efx");
	p = [];
	p[p.size] = (4400, 2500, 80);	p[p.size] = (3500, 2500, 80);	p[p.size] = (5400, 2600, 80);
	p[p.size] = (-1800, -1200, 80);	p[p.size] = (-6000, -4200, 120);	p[p.size] = (-3000, -3300, 80);
	p[p.size] = (1000, 1500, 100);	p[p.size] = (6800, 2400, 100);	p[p.size] = (0, -2000, 100);
	for (i = 0; i < p.size; i++)
		maps\_fx::loopfx("kum_ruzgar", p[i], 1.4, p[i] + (0, 0, 100));
}

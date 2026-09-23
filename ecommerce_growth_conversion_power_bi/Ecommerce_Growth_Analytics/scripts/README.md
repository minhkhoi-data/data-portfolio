# Dataset generation

The bundled demo data was created deterministically for portfolio use.

Seed: `20260916`

The generator intentionally creates:
- holiday traffic and revenue seasonality
- channel-level conversion differences
- a mobile vs desktop conversion gap
- higher returning-user conversion
- realistic order-item product mix

It is designed for BI modelling practice, not for statistical inference about Google.

The full generation logic used to create the repository is documented in the project README and can be regenerated from the source package supplied with the project.

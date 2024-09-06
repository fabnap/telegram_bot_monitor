# following the convention:
# name low crit low warning high warning high critical
WPGas = 1.25
WPtmpA = 24.5
WPtmpB = 24.0
WPtmpC = 25.0
alarms_dict = {
"pressure": [WPGas * 0.9 ,WPGas * 0.95  ,WPGas * 1.05 ,WPGas * 1.1  ],
"vacuum":   [0.0  ,0.0  ,5e-6  ,1e-5  ],
"tsdd1":   [-160  ,-160 ,-100  ,-100  ],
"tsdd2":   [-160 ,-160  ,-100  ,-100  ],
"tsdd3":   [-160 ,-160  ,-100  ,-100  ],
"tsdd4":   [-160 ,-160 ,-100  ,-100  ],
"tsdd5":   [-160 ,-160 ,-100  ,-100  ],
"tsdd6":   [-160 ,-160 ,-100  ,-100  ],
"tsdda":   [WPtmpA-2  ,WPtmpA-1  ,WPtmpA+1  ,WPtmpA+2],
"tsddb":   [WPtmpB-2  ,WPtmpB-1  ,WPtmpB+1  ,WPtmpB+2],# important
"tsddc":   [WPtmpC-2  ,WPtmpC-1  ,WPtmpC+1  ,WPtmpC+2],
"tsddd":   [0.0  ,0.0  ,76    ,77    ],
"tsdr1":   [121  ,123  ,129    ,131  ], # important
"tsdr2":   [121  ,123  ,129    ,131  ], # important

}

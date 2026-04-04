import json

# Espresso Charts - Week of April 6, 2026 (v7)
# Stories:
#   0: Artemis II - 53 Years Back to the Moon
#   1: 27 Million Tons of Invisible Plastic
#   2: Arctic Sea Ice Ties Record Low (Again)

config = json.loads(r'''
{
  "week": {
    "year": "2026",
    "month": "04",
    "week_start": "06"
  },
  "defaults": {
    "face_color": "#F5F0E6",
    "dpi": 200,
    "px_width": 1080,
    "px_height": 1350,
    "suptitle_font": "Playfair Display",
    "subtitle_font": "Source Serif 4",
    "voiceover": {
      "voice_name": "bella",
      "model": "multilingual_v2",
      "stability": 0.5,
      "speed": 0.95
    },
    "audio_mix": {
      "vo_delay": 0.5,
      "vo_volume": 1.0,
      "music_volume": 0.5,
      "music_fade_in": 0.1,
      "music_fade_out": 0.1
    }
  },
  "stories": [
    {
      "id": 0,
      "slug": "artemis_ii_53_years",
      "cover": {
        "txt_suptitle": "53\nyears",
        "txt_subtitle": "The gap between the last crew to leave\nlow Earth orbit and the next one.",
        "suptitle_size": 86,
        "subtitle_size": 18,
        "accent_line_color": "#3F5B83",
        "txt_unit": "between Moon missions",
        "txt_eyebrow": "Human Spaceflight · 2026",
        "txt_issue": "001",
        "show_corner_mark": true
      },
      "charts": [
        {
          "type": "bar",
          "data_date": "2026-04-01",
          "data": {
            "Object": [
              "Int'l Space Station",
              "Hubble Telescope",
              "GPS Satellites",
              "Apollo 11 Landing",
              "Artemis II Max Distance"
            ],
            "Distance_mi": [
              254,
              340,
              12550,
              238855,
              252000
            ]
          },
          "params": {
            "col_dim": "Object",
            "col_measure": "Distance_mi",
            "txt_suptitle": "Artemis II Will Travel\n252,000 Miles from Earth",
            "txt_subtitle": "How far is that? A comparison of\nobjects and missions by distance.",
            "txt_label": "Source: NASA\nhttps://science.nasa.gov",
            "num_format": "{:,.0f} mi",
            "num_divisor": 1,
            "bar_color": "#3F5B83",
            "bar_colors": {
              "0": "#CDAF7B",
              "1": "#CDAF7B",
              "2": "#CDAF7B",
              "3": "#4D5523",
              "4": "#3F5B83"
            },
            "suptitle_size": 26,
            "subtitle_size": 14,
            "label_size": 10,
            "suptitle_y_custom": 0.99,
            "subtitle_pad_custom": 60,
            "suptitle_font": "Playfair Display",
            "subtitle_font": "Source Serif 4",
            "factor_limit_x": 1.25,
            "hide_left_spine": true,
            "value_label_offset_x": {
              "0": 160,
              "1": 140,
              "2": 100
            }
          }
        },
        {
          "type": "bar",
          "data_date": "2026-04-01",
          "data": {
            "Object": [
              "Commercial jet",
              "Speed of sound",
              "Rifle bullet",
              "ISS orbital speed",
              "Artemis II reentry"
            ],
            "Speed_mph": [
              575,
              767,
              1700,
              17500,
              25000
            ]
          },
          "params": {
            "col_dim": "Object",
            "col_measure": "Speed_mph",
            "txt_suptitle": "Artemis II Will Reenter\nat 25,000 mph",
            "txt_subtitle": "Fastest human reentry ever attempted.\nFaster than a rifle bullet by 15x.",
            "txt_label": "Source: NASA\nhttps://www.nasa.gov/artemis-ii",
            "num_format": "{:,.0f} mph",
            "num_divisor": 1,
            "bar_color": "#A14516",
            "bar_colors": {
              "0": "#CDAF7B",
              "1": "#CDAF7B",
              "2": "#CDAF7B",
              "3": "#4D5523",
              "4": "#A14516"
            },
            "suptitle_size": 26,
            "subtitle_size": 14,
            "label_size": 10,
            "suptitle_y_custom": 0.99,
            "subtitle_pad_custom": 60,
            "suptitle_font": "Playfair Display",
            "subtitle_font": "Source Serif 4",
            "factor_limit_x": 1.25,
            "hide_left_spine": true,
            "value_label_offset_x": {
              "0": 120,
              "1": 110,
              "2": 80
            }
          }
        },
        {
          "type": "bar",
          "data_date": "2026-04-01",
          "data": {
            "Rocket": [
              "Falcon 9",
              "Falcon Heavy",
              "Space Shuttle",
              "Saturn V",
              "SLS Block 1"
            ],
            "Thrust_Mlbs": [
              1.7,
              5.1,
              6.8,
              7.6,
              8.8
            ]
          },
          "params": {
            "col_dim": "Rocket",
            "col_measure": "Thrust_Mlbs",
            "txt_suptitle": "The SLS Is the Most Powerful\nRocket Ever to Fly",
            "txt_subtitle": "Liftoff thrust in millions of pounds.\nSLS Block 1 surpasses Saturn V.",
            "txt_label": "Source: NASA\nhttps://www.nasa.gov/sls",
            "num_format": "{:.1f}M lbs",
            "num_divisor": 1,
            "bar_color": "#3F5B83",
            "bar_colors": {
              "0": "#CDAF7B",
              "1": "#CDAF7B",
              "2": "#CDAF7B",
              "3": "#4D5523",
              "4": "#3F5B83"
            },
            "suptitle_size": 26,
            "subtitle_size": 14,
            "label_size": 10,
            "suptitle_y_custom": 0.99,
            "subtitle_pad_custom": 60,
            "suptitle_font": "Playfair Display",
            "subtitle_font": "Source Serif 4",
            "factor_limit_x": 1.2,
            "hide_left_spine": true
          }
        }
      ],
      "reel": {
        "animated_charts": [
          {
            "type": "cover_animate",
            "params": {
              "txt_suptitle": "53\nyears",
              "txt_subtitle": "The gap between the last crew to leave\nlow Earth orbit and the next one.",
              "suptitle_size": 86,
              "subtitle_size": 18,
              "suptitle_y": 0.65,
              "subtitle_y": 0.38,
              "accent_line_color": "#3F5B83",
              "suptitle_font": "Playfair Display",
              "subtitle_font": "Source Serif 4",
              "face_color": "#F5F0E6",
              "txt_unit": "between Moon missions",
              "txt_eyebrow": "Human Spaceflight · 2026",
              "txt_issue": "001",
              "show_corner_mark": true,
              "count_up": true,
              "duration": 3.5,
              "hold_duration": 2.0
            }
          },
          {
            "type": "bar_animate",
            "data": {
              "Object": [
                "Int'l Space Station",
                "Hubble Telescope",
                "GPS Satellites",
                "Apollo 11 Landing",
                "Artemis II Max Distance"
              ],
              "Distance_mi": [
                254,
                340,
                12550,
                238855,
                252000
              ]
            },
            "params": {
              "col_dim": "Object",
              "col_measure": "Distance_mi",
              "txt_suptitle": "Artemis II Will Travel\n252,000 Miles from Earth",
              "txt_subtitle": "How far is that? A comparison\nby distance from Earth.",
              "txt_label": "Source: NASA",
              "num_format": "{:,.0f} mi",
              "num_divisor": 1,
              "bar_color": "#3F5B83",
              "bar_colors": {
                "0": "#CDAF7B",
                "1": "#CDAF7B",
                "2": "#CDAF7B",
                "3": "#4D5523",
                "4": "#3F5B83"
              },
              "suptitle_size": 24,
              "subtitle_size": 13,
              "label_size": 10,
              "suptitle_y_custom": 0.93,
              "subtitle_pad_custom": 60,
              "suptitle_font": "Playfair Display",
              "subtitle_font": "Source Serif 4",
              "factor_limit_x": 1.25,
              "hide_left_spine": true,
              "value_label_offset_x": {
                "0": 160,
                "1": 140,
                "2": 100
              },
              "duration": 14,
              "hold_frames": 150,
              "px_width": 1080,
              "px_height": 1920,
              "face_color": "#F5F0E6"
            }
          }
        ],
        "voiceover": {
          "text": "The International Space Station orbits at two hundred and fifty-four miles. GPS satellites sit at twelve thousand. The Moon is two hundred and thirty-nine thousand miles away. Artemis Two will fly past it, reaching two hundred and fifty-two thousand miles from Earth. Farther than any human has ever traveled."
        },
        "music": {
          "preset": "editorial_minimal",
          "duration_ms": 28000
        }
      },
      "story_files": [
        [
          0,
          0,
          "story_0_cover",
          "png"
        ],
        [
          0,
          1,
          "story_0_chart_1",
          "png"
        ],
        [
          0,
          2,
          "story_0_chart_2",
          "png"
        ],
        [
          0,
          3,
          "story_0_chart_3",
          "png"
        ],
        [
          0,
          4,
          "story_0_reel_with_voice",
          "mp4"
        ]
      ],
      "copy": {
        "instagram": {
          "caption": "Artemis II will travel 252,000 miles from Earth. That is roughly a thousand times farther than the International Space Station.\n\nThe ISS orbits at 254 miles. GPS satellites sit at 12,550. The Apollo 11 landing site was 238,855 miles away. Artemis II will fly 4,700 miles past the Moon, farther than any human has ever been.\n\nWhen the Orion capsule returns, it will hit Earth's atmosphere at 25,000 mph, the fastest human reentry ever attempted. About 15 times faster than a rifle bullet. The heat shield must handle 5,000 degrees.\n\nThe rocket that got them there, the Space Launch System, produces 8.8 million pounds of thrust at liftoff. More than the Saturn V. More than any rocket ever flown.\n\nFour astronauts are aboard: Reid Wiseman, Victor Glover, Christina Koch, and Jeremy Hansen. Glover is the first person of color beyond Earth orbit. Koch is the first woman. Hansen is the first non-American on a NASA lunar flight.\n\nSubscribe for the full story: espressocharts.substack.com ☕",
          "hashtags": "#ArtemisII #NASA #Moon #Space #SpaceExploration #DataVisualization #Infographic #Science #Apollo #HumanSpaceflight #OrionSpacecraft #ChristinaKoch #VictorGlover #DataJournalism #EspressoCharts"
        },
        "instagram_reel": {
          "caption": "252,000 miles from Earth. A thousand times farther than the ISS. Farther than any human has ever traveled. Artemis II is on its way.\n\nSubscribe for the full story: espressocharts.substack.com ☕",
          "hashtags": "#ArtemisII #NASA #Moon #Space #DataViz #EspressoCharts"
        },
        "youtube_shorts": {
          "title": "Only 28 People Have Traveled Beyond Earth Orbit | Artemis II Data",
          "description": "For 53 years, only 24 people had traveled beyond low Earth orbit. All Apollo astronauts. In April 2026, Artemis II added four more to the list, including the first woman and first person of color to fly to the Moon.\n\nData from NASA. Charts by Espresso Charts.",
          "hashtags": "#ArtemisII #NASA #Moon #Space #DataVisualization #Shorts"
        },
        "substack_article": {
          "headline": "53 Years Back to the Moon",
          "subhead": "Only 28 people have ever left low Earth orbit. After a half-century pause, four more just joined the list.",
          "body": "### 53 Years Back to the Moon\n*Only 28 people have ever left low Earth orbit. After a half-century pause, four more just joined the list.*\n\nAt 6:35 p.m. Eastern on April 1, 2026, the Space Launch System rocket lifted off from Kennedy Space Center in Florida, carrying four astronauts on a 10-day journey around the Moon. The last time humans made this trip, the year was 1972.\n\n### The Distance\n\nTo appreciate the scale: the International Space Station orbits at 254 miles. GPS satellites sit at 12,550 miles. The Moon is roughly a thousand times farther than the ISS. At its maximum distance, Artemis II will be about 4,700 miles past the Moon, farther from Earth than any human has ever been.\n\n![Chart: Artemis II Will Travel 252,000 Miles from Earth](story_0_chart_1.png)\n\nThe Orion spacecraft will travel on a free-return trajectory, using lunar gravity to swing around the far side and head back to Earth. Splashdown in the Pacific is expected on April 10.\n\n### The Speed\n\nWhen Orion returns to Earth, it will hit the atmosphere at roughly 25,000 mph, the fastest human reentry ever attempted. That is about 33 times the speed of sound and 15 times faster than a rifle bullet. The heat shield must withstand temperatures around 5,000 degrees Fahrenheit.\n\n![Chart: Artemis II Will Reenter at 25,000 mph](story_0_chart_2.png)\n\n### The Rocket\n\nThe Space Launch System that carried the crew to orbit produces 8.8 million pounds of thrust at liftoff, making it the most powerful rocket ever to fly. That surpasses even the Saturn V that carried Apollo astronauts to the Moon, which produced 7.6 million pounds. SpaceX's Falcon Heavy, the most powerful commercial rocket in service, generates 5.1 million.\n\n![Chart: The SLS Is the Most Powerful Rocket Ever to Fly](story_0_chart_3.png)\n\n### The Crew\n\nBefore Artemis II, exactly 24 unique individuals had traveled beyond low Earth orbit. All flew during the Apollo program between 1968 and 1972.\n\nArtemis II adds four: Commander Reid Wiseman, Pilot Victor Glover, Mission Specialist Christina Koch, and Canadian Space Agency astronaut Jeremy Hansen. Glover is the first person of color to fly beyond Earth orbit. Koch is the first woman. Hansen is the first non-American to travel to the lunar vicinity on a NASA mission.\n\nThe total now stands at 28. That is roughly 4% of the approximately 680 people who have ever been to space.\n\n### What Comes Next\n\nArtemis II is a test flight. No landing. The crew will validate life-support systems, navigation, and manual piloting procedures that are essential for Artemis III, which aims to put astronauts on the lunar surface in 2028.\n\nFor now, the number is 28. After more than half a century, it is finally growing again.\n\n---\n*Sources: NASA Artemis II mission page (https://www.nasa.gov/artemis-ii), The Planetary Society (https://www.planetary.org)*\n*Charts and analysis: Espresso Charts*\n\n**Tags:** space, artemis, nasa, moon, human-spaceflight, data-visualization",
          "tags": "space, artemis, nasa, moon, human-spaceflight",
          "publish_at": null
        },
        "substack_chart_notes": [
          {
            "day": "Mon",
            "text": "Artemis II will travel 252,000 miles from Earth. The International Space Station orbits at 254 miles. GPS satellites sit at 12,550. The Moon is roughly a thousand times farther than the ISS. At peak distance, Artemis II will be 4,700 miles past the Moon, farther than any human has ever been.\n\nSubscribe for the full story: espressocharts.substack.com ☕",
            "image_asset": "story_0_chart_1.png"
          },
          {
            "day": "Tue",
            "text": "When Orion returns to Earth, it will hit the atmosphere at 25,000 mph. That is 33 times the speed of sound and about 15 times faster than a rifle bullet. No crewed spacecraft has ever attempted reentry at this velocity.\n\nSubscribe for the full story: espressocharts.substack.com ☕",
            "image_asset": "story_0_chart_2.png"
          }
        ]
      },
      "poster": {
        "hero_number": "53",
        "hero_unit": "years",
        "hero_eyebrow": "THE GAP BETWEEN MOON MISSIONS",
        "insight_text": "The ISS orbits at 254 miles. GPS satellites\nat 12,550. Artemis II will travel 252,000\nmiles, past the far side of the Moon.",
        "insight_context": "At peak distance, Artemis II will be 4,700 miles\nbeyond the Moon. Farther from Earth than any\nhuman has ever traveled. The last crew to make\na similar journey flew in December 1972.",
        "chart_x": [
          1968,
          1969,
          1969.5,
          1970,
          1971,
          1971.5,
          1972,
          1972.9,
          2026
        ],
        "chart_y": [
          8,
          10,
          11,
          13,
          14,
          15,
          16,
          17,
          28
        ],
        "chart_x_labels": [
          [
            1968,
            "1968"
          ],
          [
            1972,
            "1972"
          ],
          [
            2026,
            "2026"
          ]
        ],
        "chart_y_labels": [
          10,
          15,
          20,
          25
        ],
        "chart_y_format": "{:.0f}",
        "chart_color": "#3F5B83",
        "annotations": [
          {
            "year": "1968",
            "value": "Apollo 8",
            "desc": "First crew\nbeyond Earth orbit",
            "color": "#4D5523",
            "chart_x": 1968,
            "chart_y": 8
          },
          {
            "year": "1972",
            "value": "Apollo 17",
            "desc": "Last Apollo\nlunar mission",
            "color": "#A14516",
            "chart_x": 1972,
            "chart_y": 17
          },
          {
            "year": "2026",
            "value": "Artemis II",
            "desc": "53.3 years later,\nfour more fly",
            "color": "#3F5B83",
            "chart_x": 2026,
            "chart_y": 28
          }
        ],
        "source_lines": [
          "SOURCE: NASA Artemis II Mission",
          "nasa.gov/artemis-ii",
          "DATA DATE: 2026-04-01"
        ],
        "issue_number": "001",
        "issue_topic": "Human Spaceflight",
        "accent_color": "#3F5B83"
      }
    },
    {
      "id": 1,
      "slug": "ocean_nanoplastics_27_million_tons",
      "cover": {
        "txt_suptitle": "27\nmillion tons",
        "txt_subtitle": "Invisible plastic in the North Atlantic alone.\nMore than all visible ocean plastic combined.",
        "suptitle_size": 86,
        "subtitle_size": 18,
        "accent_line_color": "#4D5523",
        "txt_unit": "of invisible nanoplastic",
        "txt_eyebrow": "Ocean Pollution · 2025",
        "txt_issue": "002",
        "show_corner_mark": true
      },
      "charts": [
        {
          "type": "bar",
          "data_date": "2026-03-29",
          "data": {
            "Category": [
              "Visible macro +\nmicro plastic\n(all oceans)",
              "Nanoplastics\n(North Atlantic only)"
            ],
            "Mass_Mt": [
              3.0,
              27.0
            ]
          },
          "params": {
            "col_dim": "Category",
            "col_measure": "Mass_Mt",
            "txt_suptitle": "The Ocean's Missing Plastic\nWas There All Along",
            "txt_subtitle": "Nanoplastics in the North Atlantic alone\noutweigh all visible ocean plastic worldwide.",
            "txt_label": "Source: NIOZ / Nature (2025)\nhttps://www.nature.com/articles/s41586-025-09218-1",
            "num_format": "{:.0f} Mt",
            "num_divisor": 1,
            "bar_color": "#4D5523",
            "bar_colors": {
              "0": "#CDAF7B",
              "1": "#4D5523"
            },
            "suptitle_size": 26,
            "subtitle_size": 14,
            "label_size": 11,
            "suptitle_y_custom": 0.99,
            "subtitle_pad_custom": 60,
            "suptitle_font": "Playfair Display",
            "subtitle_font": "Source Serif 4",
            "factor_limit_x": 1.3,
            "bar_height": 0.6,
            "hide_left_spine": true,
            "value_label_offset_x": {
              "0": 160
            }
          }
        },
        {
          "type": "stem",
          "data_date": "2026-03-29",
          "data": {
            "Depth": [
              "Surface\n(10m)",
              "Mid-depth\n(1,000m)",
              "Seafloor\n(~3,000m)"
            ],
            "Concentration": [
              18.1,
              10.9,
              5.5
            ]
          },
          "params": {
            "col_dim": "Depth",
            "col_measure_a": "Concentration",
            "txt_suptitle": "Nanoplastics Found\nat Every Ocean Depth",
            "txt_subtitle": "Average concentration in mg per cubic\nmeter across 12 North Atlantic sites.",
            "txt_label": "Source: NIOZ / Nature (2025)\nhttps://www.nature.com/articles/s41586-025-09218-1",
            "num_format": "{:.1f}",
            "color_a": "#4D5523",
            "rotate_labels": false,
            "y_min": 0,
            "y_max": 24,
            "suptitle_y": 1.06,
            "subtitle_y": 0.85,
            "subtitle_pad": 40,
            "labelpad": 10,
            "suptitle_size": 26,
            "subtitle_size": 14,
            "label_size": 11,
            "value_label_offset_pts": 12,
            "marker_size": 7,
            "line_width": 2.5,
            "line_format_a": "-",
            "x_tick_label_y_offset": -0.06,
            "xtick_align_ha": "center",
            "xtick_align_va": "bottom",
            "suptitle_font": "Playfair Display",
            "subtitle_font": "Source Serif 4"
          }
        },
        {
          "type": "donut",
          "data_date": "2026-03-29",
          "data": {
            "Type": [
              "PET\n(bottles,\npackaging)",
              "Polystyrene\n(food\ncontainers)",
              "PVC\n(pipes,\npackaging)"
            ],
            "Share": [
              45,
              30,
              25
            ]
          },
          "params": {
            "col_value": "Share",
            "col_label": "Type",
            "txt_suptitle": "What the Invisible\nPlastic Is Made Of",
            "txt_subtitle": "Three polymer types dominate\nthe nanoplastic found in the Atlantic.",
            "txt_label": "Source: NIOZ / Nature (2025)\nhttps://www.nature.com/articles/s41586-025-09218-1",
            "num_format": "{:.0f}%",
            "suptitle_size": 26,
            "subtitle_size": 14,
            "subtitle_y": 0.9,
            "label_size": 10,
            "bottom_note_size": 9,
            "wedge_width": 0.4,
            "pct_colors": [
              "#FFFFFF",
              "#FFFFFF",
              "#4b2e1a"
            ],
            "colors": [
              "#3F5B83",
              "#A14516",
              "#CDAF7B"
            ],
            "instagram_format": "4x5",
            "px": 1080,
            "suptitle_font": "Playfair Display",
            "subtitle_font": "Source Serif 4"
          }
        },
        {
          "type": "line",
          "data_date": "2026-03-29",
          "data_source": [
            {
              "url": "https://raw.githubusercontent.com/owid/etl/master/etl/steps/data/garden/oecd/2024-09-12/plastic_use_projections/plastic_use_projections.csv",
              "format": "csv",
              "pick": [
                "year",
                "plastic_production"
              ],
              "rename": {
                "year": "Year",
                "plastic_production": "Production_Mt"
              },
              "types": {
                "Production_Mt": "float"
              },
              "filter": {
                "country": "World"
              }
            }
          ],
          "post": {
            "sort_by": "Year",
            "dropna": true
          },
          "data": {
            "Year": [
              1950,
              1960,
              1970,
              1980,
              1990,
              2000,
              2010,
              2020,
              2024
            ],
            "Production_Mt": [
              2,
              8,
              35,
              70,
              120,
              213,
              334,
              400,
              430
            ]
          },
          "params": {
            "col_dim": "Year",
            "col_measure_list": [
              "Production_Mt"
            ],
            "txt_suptitle": "Global Plastic Production\nGrew 200x Since 1950",
            "txt_subtitle": "Annual production in millions of tons.\n79% ends up in landfills or the environment.",
            "txt_label": "Source: OECD Global Plastics Outlook\nhttps://www.oecd.org/en/topics/plastics.html",
            "pos_text": [
              0,
              -1
            ],
            "pos_label": null,
            "show_y_axis": false,
            "bottom_note_size": 9,
            "num_format": "{:.0f} Mt",
            "line_colors": [
              "#4D5523"
            ],
            "line_widths": [
              3
            ],
            "x_ticks": [
              1950,
              1970,
              1990,
              2010,
              2024
            ],
            "x_tick_labels": [
              "1950",
              "1970",
              "1990",
              "2010",
              "2024"
            ],
            "px": 1080,
            "py": 1350,
            "suptitle_size": 26,
            "subtitle_size": 14,
            "y_limits": [
              0,
              500
            ],
            "suptitle_y": 1.2,
            "subtitle_y": 1.09,
            "text_offset_y": [
              10
            ],
            "suptitle_font": "Playfair Display",
            "subtitle_font": "Source Serif 4"
          }
        }
      ],
      "reel": {
        "animated_charts": [
          {
            "type": "cover_animate",
            "params": {
              "txt_suptitle": "27\nmillion tons",
              "txt_subtitle": "Invisible plastic in the North Atlantic alone.\nMore than all visible ocean plastic combined.",
              "suptitle_size": 86,
              "subtitle_size": 18,
              "suptitle_y": 0.65,
              "subtitle_y": 0.38,
              "accent_line_color": "#4D5523",
              "suptitle_font": "Playfair Display",
              "subtitle_font": "Source Serif 4",
              "face_color": "#F5F0E6",
              "txt_unit": "of invisible nanoplastic",
              "txt_eyebrow": "Ocean Pollution · 2025",
              "txt_issue": "002",
              "show_corner_mark": true,
              "count_up": true,
              "duration": 3.5,
              "hold_duration": 2.0
            }
          },
          {
            "type": "bar_animate",
            "data": {
              "Category": [
                "Visible plastic\n(all oceans)",
                "Nanoplastics\n(N. Atlantic only)"
              ],
              "Mass_Mt": [
                3.0,
                27.0
              ]
            },
            "params": {
              "col_dim": "Category",
              "col_measure": "Mass_Mt",
              "txt_suptitle": "The Ocean's Missing Plastic\nWas There All Along",
              "txt_subtitle": "Nanoplastics in the North Atlantic\noutweigh all visible ocean plastic.",
              "txt_label": "Source: NIOZ / Nature",
              "num_format": "{:.0f} Mt",
              "bar_color": "#4D5523",
              "bar_colors": {
                "0": "#CDAF7B",
                "1": "#4D5523"
              },
              "suptitle_size": 24,
              "subtitle_size": 13,
              "label_size": 11,
              "suptitle_y_custom": 0.93,
              "subtitle_pad_custom": 60,
              "factor_limit_x": 1.3,
              "bar_height": 0.6,
              "hide_left_spine": true,
              "value_label_offset_x": {
                "0": 160
              },
              "duration": 14,
              "hold_frames": 180,
              "px_width": 1080,
              "px_height": 1920,
              "suptitle_font": "Playfair Display",
              "subtitle_font": "Source Serif 4",
              "face_color": "#F5F0E6"
            }
          }
        ],
        "voiceover": {
          "text": "Scientists just solved the mystery of the ocean's missing plastic. It did not disappear. It shrank. Twenty-seven million tons of nanoplastics, particles smaller than a micrometer, are floating in the North Atlantic alone. That is nine times more than all visible plastic in every ocean on Earth combined."
        },
        "music": {
          "preset": "lofi_coffee",
          "duration_ms": 29000
        }
      },
      "story_files": [
        [
          1,
          0,
          "story_1_cover",
          "png"
        ],
        [
          1,
          1,
          "story_1_chart_1",
          "png"
        ],
        [
          1,
          2,
          "story_1_chart_2",
          "png"
        ],
        [
          1,
          3,
          "story_1_chart_3",
          "png"
        ],
        [
          1,
          4,
          "story_1_chart_4",
          "png"
        ],
        [
          1,
          5,
          "story_1_reel_with_voice",
          "mp4"
        ]
      ],
      "copy": {
        "instagram": {
          "caption": "27 million tons of plastic are floating in the North Atlantic. You cannot see any of it.\n\nScientists at the Royal Netherlands Institute for Sea Research published the first estimate of nanoplastics in ocean water. These particles are smaller than one micrometer, roughly one-hundredth the width of a human hair.\n\nThe finding solves a long-standing mystery: where did all the plastic go? Global production exceeds 430 million tons per year. Only a fraction has been accounted for in the environment. The answer is that much of it broke down into particles too small to detect until now.\n\nThe 27 million tons of nanoplastics in the North Atlantic alone outweigh all visible macro and microplastic floating in every ocean on Earth, estimated at around 3 million tons total.\n\nThe three dominant types: PET (bottles and packaging), polystyrene (food containers), and PVC. They were found at every depth, from the surface to the seafloor, at all 12 sampling locations.\n\nThese particles cannot be cleaned up. They have entered the food chain, the atmosphere, and human tissue, including the brain.\n\nSubscribe for the full story: espressocharts.substack.com ☕",
          "hashtags": "#Nanoplastics #OceanPollution #PlasticPollution #DataVisualization #Environment #Science #Ocean #Microplastics #ClimateAction #DataJournalism #Research #NIOZ #Nature #Infographic #EspressoCharts"
        },
        "instagram_reel": {
          "caption": "27 million tons of invisible plastic in one ocean. Nine times more than all visible plastic in every ocean combined. The ocean's missing plastic was there all along, just too small to see.\n\nSubscribe for the full story: espressocharts.substack.com ☕",
          "hashtags": "#Nanoplastics #OceanPollution #PlasticPollution #DataViz #Science #EspressoCharts"
        },
        "youtube_shorts": {
          "title": "27 Million Tons of Invisible Plastic Found in the Ocean | Data Explained",
          "description": "Scientists just measured nanoplastics in the ocean for the first time. 27 million tons in the North Atlantic alone, nine times more than all visible ocean plastic worldwide. Data from NIOZ and Nature. Charts by Espresso Charts.",
          "hashtags": "#Nanoplastics #OceanPollution #Science #DataVisualization #Environment #Shorts"
        },
        "substack_article": {
          "headline": "27 Million Tons of Invisible Plastic",
          "subhead": "Scientists solved the mystery of the ocean's missing plastic. It shrank.",
          "body": "### 27 Million Tons of Invisible Plastic\n*Scientists solved the mystery of the ocean's missing plastic. It shrank.*\n\nFor years, a puzzle has nagged ocean scientists. Humanity produces over 430 million tons of plastic every year. Roughly 79% ends up in landfills or the natural environment. Between 400,000 and 4 million tons flow into the oceans annually. Yet when researchers tried to account for all that plastic, the numbers did not add up. Much of it appeared to have vanished.\n\nA study published in Nature by researchers at the Royal Netherlands Institute for Sea Research (NIOZ) and Utrecht University has found the answer. The plastic did not disappear. It broke down into particles too small to see.\n\n### The First Estimate\n\nThe research team collected water samples at 12 locations across the North Atlantic, from the subtropical gyre to the European continental shelf. At each site they sampled at three depths: near the surface, at roughly 1,000 meters, and near the seafloor.\n\nUsing mass spectrometry techniques borrowed from atmospheric science, they measured nanoplastics, particles smaller than one micrometer (one-thousandth of a millimeter). They found them at every location and every depth.\n\nScaled across the North Atlantic, the team estimates approximately 27 million tons of nanoplastics in the surface mixed layer alone. For context, the estimated total mass of all visible macro and microplastic floating in every ocean on Earth is roughly 3 million tons. The invisible fraction in one ocean basin outweighs the visible fraction worldwide by a factor of nine.\n\n![Chart: The Ocean's Missing Plastic Was There All Along](story_1_chart_1.png)\n\nConcentrations were highest near the surface at 18.1 milligrams per cubic meter, declining to 10.9 at mid-depth and 5.5 near the seafloor.\n\n![Chart: Nanoplastics Found at Every Ocean Depth](story_1_chart_2.png)\n\n### What It Is Made Of\n\nThree polymer types dominate: polyethylene terephthalate (PET), the material in water bottles and food packaging; polystyrene, used in takeaway containers and insulation; and polyvinyl chloride (PVC), common in pipes and packaging.\n\n![Chart: What the Invisible Plastic Is Made Of](story_1_chart_3.png)\n\n### Where It Comes From\n\nNanoplastics reach the ocean through three main pathways. Larger plastic fragments degrade under ultraviolet sunlight. River systems carry particles from land. And atmospheric transport deposits nanoplastics through rainfall and dry deposition.\n\nGlobal plastic production has grown roughly 200-fold since 1950, from about 2 million tons per year to 430 million. The OECD's Global Plastics Outlook projects continued growth unless policy interventions change the trajectory.\n\n![Chart: Global Plastic Production Grew 200x Since 1950](story_1_chart_4.png)\n\n### What It Means\n\nNanoplastics have already been detected in human brain tissue, blood, and placenta. Their small size allows them to cross biological barriers that larger microplastics cannot. The ecological and health implications remain an active area of research.\n\nOne thing is clear from the NIOZ data: cleanup is not a realistic option at this scale. As lead researcher Helge Niemann put it, the nanoplastics that are already in the ocean can never be removed. Prevention, not remediation, is the only path forward.\n\n---\n*Sources: NIOZ / Nature (https://www.nature.com/articles/s41586-025-09218-1), OECD Global Plastics Outlook (https://www.oecd.org/en/topics/plastics.html)*\n*Charts and analysis: Espresso Charts*\n\n**Tags:** environment, ocean, plastic-pollution, nanoplastics, science, data-visualization",
          "tags": "environment, ocean, plastic-pollution, nanoplastics, science",
          "publish_at": null
        },
        "substack_chart_notes": [
          {
            "day": "Wed",
            "text": "Scientists at NIOZ estimate 27 million tons of nanoplastics in the North Atlantic surface layer. All visible plastic floating in every ocean on Earth totals about 3 million tons. The invisible fraction in one ocean basin is nine times larger than the visible fraction worldwide.\n\nSubscribe for the full story: espressocharts.substack.com ☕",
            "image_asset": "story_1_chart_1.png"
          },
          {
            "day": "Thu",
            "text": "Nanoplastics were detected at every depth researchers sampled in the North Atlantic: 18.1 mg per cubic meter near the surface, 10.9 at 1,000 meters, and 5.5 near the seafloor. There is no layer of the ocean that has been spared.\n\nSubscribe for the full story: espressocharts.substack.com ☕",
            "image_asset": "story_1_chart_2.png"
          }
        ]
      },
      "poster": {
        "hero_number": "27",
        "hero_unit": "million tons",
        "hero_eyebrow": "INVISIBLE PLASTIC IN ONE OCEAN",
        "insight_text": "The ocean's missing plastic was there\nall along. It shrank to particles smaller\nthan one micrometer.",
        "insight_context": "27 million tons of nanoplastics float in the\nNorth Atlantic surface layer. All visible plastic\nin every ocean on Earth totals about 3 million tons.\nThe invisible fraction is nine times larger.",
        "chart_x_labels": [
          [
            1950,
            "1950"
          ],
          [
            1970,
            "1970"
          ],
          [
            1990,
            "1990"
          ],
          [
            2010,
            "2010"
          ],
          [
            2024,
            "Now"
          ]
        ],
        "chart_y_labels": [
          100,
          200,
          300,
          400
        ],
        "chart_y_format": "{:.0f} Mt",
        "chart_color": "#4D5523",
        "annotations": [
          {
            "year": "1950",
            "value": "2 Mt/yr",
            "desc": "Global plastic\nproduction begins",
            "color": "#CDAF7B",
            "chart_x": 1950,
            "chart_y": 2
          },
          {
            "year": "2000",
            "value": "213 Mt/yr",
            "desc": "Production\npasses 200 Mt",
            "color": "#3F5B83",
            "chart_x": 2000,
            "chart_y": 213
          },
          {
            "year": "2024",
            "value": "430 Mt/yr",
            "desc": "200x growth\nin 74 years",
            "color": "#4D5523",
            "chart_x": 2024,
            "chart_y": 430
          }
        ],
        "source_lines": [
          "SOURCE: NIOZ / Nature (2025)",
          "nature.com/articles/s41586-025-09218-1",
          "DATA DATE: 2026-03-29"
        ],
        "issue_number": "002",
        "issue_topic": "Ocean Nanoplastics",
        "accent_color": "#4D5523"
      }
    },
    {
      "id": 2,
      "slug": "arctic_sea_ice_record_low_2026",
      "cover": {
        "txt_suptitle": "-13%\nsince 1979",
        "txt_subtitle": "Arctic winter sea ice peaked at its lowest\non record, for the second consecutive year.",
        "suptitle_size": 86,
        "subtitle_size": 18,
        "accent_line_color": "#A14516",
        "txt_unit": "Arctic winter ice decline",
        "txt_eyebrow": "Arctic Sea Ice · 2026",
        "txt_issue": "003",
        "show_corner_mark": true
      },
      "charts": [
        {
          "type": "line",
          "data_date": "2026-03-26",
          "data": {
            "Year": [
              1979,
              1985,
              1990,
              1995,
              2000,
              2005,
              2010,
              2015,
              2020,
              2025,
              2026
            ],
            "Max_Extent_Mkm2": [
              16.5,
              16.2,
              16.0,
              15.7,
              15.6,
              15.3,
              15.1,
              14.7,
              14.8,
              14.31,
              14.29
            ]
          },
          "params": {
            "col_dim": "Year",
            "col_measure_list": [
              "Max_Extent_Mkm2"
            ],
            "txt_suptitle": "Arctic Winter Sea Ice Hit\nIts Lowest Peak on Record",
            "txt_subtitle": "Annual maximum extent in millions of km².\nDashed line = 1981-2010 average (15.6M).",
            "txt_label": "Source: NSIDC / NASA\nhttps://nsidc.org",
            "pos_text": [
              0,
              -1
            ],
            "pos_label": null,
            "show_y_axis": false,
            "bottom_note_size": 9,
            "num_format": "{:.1f}",
            "line_colors": [
              "#3F5B83"
            ],
            "line_widths": [
              3
            ],
            "x_ticks": [
              1979,
              1990,
              2000,
              2010,
              2020,
              2026
            ],
            "x_tick_labels": [
              "1979",
              "1990",
              "2000",
              "2010",
              "2020",
              "2026"
            ],
            "px": 1080,
            "py": 1350,
            "suptitle_size": 26,
            "subtitle_size": 14,
            "y_limits": [
              13.5,
              17.0
            ],
            "suptitle_y": 1.2,
            "subtitle_y": 1.09,
            "text_offset_y": [
              0.15
            ],
            "suptitle_font": "Playfair Display",
            "subtitle_font": "Source Serif 4",
            "hlines": [
              {
                "y": 15.6,
                "color": "#CDAF7B",
                "style": "--",
                "width": 0.9,
                "alpha": 0.5,
                "label": "",
                "label_color": "#CDAF7B",
                "label_size": 9
              }
            ]
          }
        },
        {
          "type": "bar",
          "data_date": "2026-03-26",
          "data": {
            "Year": [
              "2026",
              "2025",
              "2018",
              "2017",
              "2016",
              "2015"
            ],
            "Deficit_km2": [
              -1310,
              -1290,
              -1210,
              -1180,
              -1160,
              -930
            ]
          },
          "params": {
            "col_dim": "Year",
            "col_measure": "Deficit_km2",
            "txt_suptitle": "Six Lowest Arctic Ice\nMaximums on Record",
            "txt_subtitle": "Deficit vs. 1981-2010 average\nin thousands of square kilometers.",
            "txt_label": "Source: NSIDC\nhttps://nsidc.org",
            "num_format": "{:,.0f}",
            "num_divisor": 1,
            "bar_color": "#3F5B83",
            "bar_colors": {
              "0": "#A14516",
              "1": "#A14516",
              "2": "#3F5B83",
              "3": "#3F5B83",
              "4": "#3F5B83",
              "5": "#3F5B83"
            },
            "suptitle_size": 26,
            "subtitle_size": 14,
            "label_size": 10,
            "suptitle_y_custom": 0.99,
            "subtitle_pad_custom": 60,
            "suptitle_font": "Playfair Display",
            "subtitle_font": "Source Serif 4",
            "factor_limit_x": 1.2,
            "show_zero_line": true,
            "zero_line_color": "#4b2e1a",
            "hide_left_spine": true
          }
        },
        {
          "type": "donut",
          "data_date": "2026-03-26",
          "data": {
            "Type": [
              "Ice older\nthan 4 years",
              "Younger ice"
            ],
            "Share": [
              5,
              95
            ]
          },
          "params": {
            "col_value": "Share",
            "col_label": "Type",
            "txt_suptitle": "95% of the Arctic's\nOldest Ice Is Gone",
            "txt_subtitle": "Multi-year ice older than four years\nhas declined by over 95% since the 1980s.",
            "txt_label": "Source: NOAA Arctic Report Card 2025\nhttps://arctic.noaa.gov/report-card",
            "num_format": "{:.0f}%",
            "suptitle_size": 26,
            "subtitle_size": 14,
            "subtitle_y": 0.9,
            "label_size": 10,
            "bottom_note_size": 9,
            "wedge_width": 0.4,
            "pct_colors": [
              "#FFFFFF",
              "#4b2e1a"
            ],
            "colors": [
              "#3F5B83",
              "#CDAF7B"
            ],
            "instagram_format": "4x5",
            "px": 1080,
            "suptitle_font": "Playfair Display",
            "subtitle_font": "Source Serif 4"
          }
        },
        {
          "type": "stem",
          "data_date": "2026-03-27",
          "data": {
            "Period": [
              "1996-2002",
              "2003-2008",
              "2009-2015",
              "2016-2023"
            ],
            "Season_Days": [
              220,
              205,
              185,
              165
            ]
          },
          "params": {
            "col_dim": "Period",
            "col_measure_a": "Season_Days",
            "txt_suptitle": "Alaska's Landfast Ice\nSeason Is Shrinking",
            "txt_subtitle": "Average days per year that stable\nice clings to Alaska's northern coast.",
            "txt_label": "Source: UAF Geophysical Institute (2026)\nhttps://www.gi.alaska.edu",
            "num_format": "{:.0f} days",
            "color_a": "#A14516",
            "rotate_labels": false,
            "y_min": 0,
            "y_max": 260,
            "suptitle_y": 1.06,
            "subtitle_y": 0.85,
            "subtitle_pad": 40,
            "labelpad": 10,
            "suptitle_size": 26,
            "subtitle_size": 14,
            "label_size": 11,
            "value_label_offset_pts": 12,
            "marker_size": 6,
            "line_width": 2.5,
            "line_format_a": "-",
            "suptitle_font": "Playfair Display",
            "subtitle_font": "Source Serif 4"
          }
        }
      ],
      "reel": {
        "animated_charts": [
          {
            "type": "cover_animate",
            "params": {
              "txt_suptitle": "-13%\nsince 1979",
              "txt_subtitle": "Arctic winter sea ice peaked at its lowest\non record, for the second consecutive year.",
              "suptitle_size": 86,
              "subtitle_size": 18,
              "suptitle_y": 0.65,
              "subtitle_y": 0.38,
              "accent_line_color": "#A14516",
              "suptitle_font": "Playfair Display",
              "subtitle_font": "Source Serif 4",
              "face_color": "#F5F0E6",
              "txt_unit": "Arctic winter ice decline",
              "txt_eyebrow": "Arctic Sea Ice · 2026",
              "txt_issue": "003",
              "show_corner_mark": true,
              "count_up": true,
              "duration": 3.5,
              "hold_duration": 2.0
            }
          },
          {
            "type": "line_animate",
            "data": {
              "Year": [
                1979,
                1985,
                1990,
                1995,
                2000,
                2005,
                2010,
                2015,
                2020,
                2025,
                2026
              ],
              "Max_Extent_Mkm2": [
                16.5,
                16.2,
                16.0,
                15.7,
                15.6,
                15.3,
                15.1,
                14.7,
                14.8,
                14.31,
                14.29
              ]
            },
            "params": {
              "col_dim": "Year",
              "col_measure_list": [
                "Max_Extent_Mkm2"
              ],
              "txt_suptitle": "Arctic Winter Sea Ice Hit\nIts Lowest Peak on Record",
              "txt_subtitle": "Annual max extent in M km².\nDashed line = 1981-2010 average (15.6M).",
              "txt_label": "Source: NSIDC / NASA",
              "pos_text": [
                -1
              ],
              "pos_label": null,
              "show_y_axis": false,
              "bottom_note_size": 9,
              "num_format": "{:.1f}",
              "line_colors": [
                "#3F5B83"
              ],
              "line_widths": [
                3
              ],
              "px": 1080,
              "py": 1920,
              "suptitle_size": 28,
              "subtitle_size": 16,
              "suptitle_y": 1.05,
              "subtitle_y": 0.97,
              "y_limits": [
                13.5,
                17.0
              ],
              "duration": 14,
              "hold_frames": 180,
              "text_offset_y": [
                0.15
              ],
              "suptitle_font": "Playfair Display",
              "subtitle_font": "Source Serif 4",
              "hlines": [
                {
                  "y": 15.6,
                  "color": "#CDAF7B",
                  "style": "--",
                  "width": 1.0,
                  "alpha": 0.5,
                  "label": "Avg",
                  "label_color": "#CDAF7B",
                  "label_size": 9
                }
              ]
            }
          }
        ],
        "voiceover": {
          "text": "Arctic winter sea ice just tied its lowest peak on record, for the second consecutive year. It peaked at fourteen point two nine million square kilometers. The missing area is twice the size of Texas. And ninety-five percent of the Arctic's oldest ice has vanished since the eighties."
        },
        "music": {
          "preset": "editorial_minimal",
          "duration_ms": 29000
        }
      },
      "story_files": [
        [
          2,
          0,
          "story_2_cover",
          "png"
        ],
        [
          2,
          1,
          "story_2_chart_1",
          "png"
        ],
        [
          2,
          2,
          "story_2_chart_2",
          "png"
        ],
        [
          2,
          3,
          "story_2_chart_3",
          "png"
        ],
        [
          2,
          4,
          "story_2_chart_4",
          "png"
        ],
        [
          2,
          5,
          "story_2_reel_with_voice",
          "mp4"
        ]
      ],
      "copy": {
        "instagram": {
          "caption": "Arctic sea ice just tied its all-time lowest winter peak. For the second consecutive year.\n\nOn March 15, 2026, sea ice extent reached 14.29 million square kilometers, according to NASA and the National Snow and Ice Data Center. That is statistically tied with the 2025 record of 14.31 million km squared, the lowest in the 48-year satellite record.\n\nThe gap between this year's peak and the 1981-2010 average is about 1.3 million square kilometers, an area roughly twice the size of Texas.\n\nThe thickness data is equally alarming. Multi-year ice, the oldest and most resilient layer older than four years, has declined by over 95% since the 1980s. The Arctic is not just losing area. It is losing structure.\n\nAlong Alaska's northern coast, landfast ice, the stable ice that anchors to the shoreline and protects communities from storms, is forming later and breaking up earlier. A 27-year analysis from the University of Alaska Fairbanks shows the season has shortened by weeks to months.\n\nA low winter maximum gives the spring melt season a head start. Less ice means less sunlight reflected, more heat absorbed, and more melting. The cycle reinforces itself.\n\nSubscribe for the full story: espressocharts.substack.com ☕",
          "hashtags": "#ArcticIce #SeaIce #ClimateChange #DataVisualization #Arctic #NASA #NSIDC #Environment #Science #ClimateData #DataJournalism #Infographic #Cryosphere #EspressoCharts"
        },
        "instagram_reel": {
          "caption": "Arctic winter sea ice tied its record low for the second year running. The missing area is twice the size of Texas. And 95% of the oldest, thickest ice has vanished since the 1980s.\n\nSubscribe for the full story: espressocharts.substack.com ☕",
          "hashtags": "#ArcticIce #SeaIce #ClimateChange #DataViz #Science #EspressoCharts"
        },
        "youtube_shorts": {
          "title": "Arctic Sea Ice Hits Record Low for 2nd Year | Climate Data 2026",
          "description": "Arctic winter sea ice peaked at 14.29M km squared on March 15, 2026, tying last year's record low. The deficit vs. average is twice the size of Texas. Multi-year ice has declined 95% since the 1980s. Data from NSIDC and NASA.",
          "hashtags": "#ArcticIce #ClimateChange #SeaIce #NASA #DataVisualization #Shorts"
        },
        "substack_article": {
          "headline": "The Arctic's Ice Keeps Setting Records, the Wrong Kind",
          "subhead": "Winter sea ice tied its lowest peak for the second consecutive year. The oldest ice has nearly vanished.",
          "body": "### The Arctic's Ice Keeps Setting Records, the Wrong Kind\n*Winter sea ice tied its lowest peak for the second consecutive year. The oldest ice has nearly vanished.*\n\nOn March 15, 2026, Arctic sea ice reached its annual winter maximum at 14.29 million square kilometers (5.52 million square miles), according to the National Snow and Ice Data Center and NASA. That figure is statistically tied with the 2025 record of 14.31 million km squared, making these two consecutive years the lowest winter peak in the 48-year satellite record.\n\n### The Trend\n\nArctic sea ice naturally expands each winter and shrinks each summer. Scientists track both the winter maximum and summer minimum as indicators of the ice system's health. The winter maximum matters because it sets the starting line for the melt season.\n\nThe 2026 peak is roughly 1.3 million square kilometers below the 1981-2010 average. That deficit is approximately twice the surface area of Texas. In 1979, when satellite records began, the winter maximum was about 16.5 million km squared. The decline since then averages about 2.6% per decade, but the pace has accelerated. The five lowest winter maximums have all occurred in the last decade.\n\n![Chart: Arctic Winter Sea Ice Hit Its Lowest Peak on Record](story_2_chart_1.png)\n\nThe six lowest winter maximums on record all fell between 2015 and 2026. The two most recent years, 2025 and 2026, sit at the bottom of the list.\n\n![Chart: Six Lowest Arctic Ice Maximums on Record](story_2_chart_2.png)\n\n### Thickness, Not Just Area\n\nExtent tells only part of the story. Ice thickness has changed even more dramatically. NASA's ICESat-2 satellite shows that much of the Arctic ice this year is thinner than usual, particularly in the Barents Sea northeast of Greenland.\n\nThe most striking figure comes from NOAA's 2025 Arctic Report Card: multi-year ice older than four years has declined by more than 95% since the 1980s. The oldest, thickest ice, which once covered vast stretches of the central Arctic, is now largely confined to a narrow band north of Greenland and the Canadian Archipelago.\n\n![Chart: 95% of the Arctic's Oldest Ice Is Gone](story_2_chart_3.png)\n\n### Alaska's Shrinking Shield\n\nA study published in January 2026 in the Journal of Geophysical Research by scientists at the University of Alaska Fairbanks examined 27 years of data on landfast ice, the stable ice that attaches to Alaska's northern coastline. They found the landfast ice season is shrinking in both time and space: forming later in the fall, breaking up earlier in the spring, and extending less far offshore.\n\n![Chart: Alaska's Landfast Ice Season Is Shrinking](story_2_chart_4.png)\n\nThis matters directly to communities. Indigenous Inupiaq communities depend on stable landfast ice for travel and subsistence hunting. Shorter ice seasons mean more dangerous conditions and greater exposure to coastal erosion from open-water storms.\n\n### The Feedback Loop\n\nA low winter maximum gives the melt season a head start. Open ocean absorbs more solar energy than reflective ice, raising surface temperatures and melting more ice in return. Scientists call this the ice-albedo feedback, and it is one of the reasons the Arctic is warming roughly three to four times faster than the global average.\n\nNSIDC scientist Walt Meier noted that one or two low years do not define a trend on their own. But viewed in the context of nearly five decades of decline, they reinforce the trajectory. The signal is consistent across extent, thickness, age, and season length. The Arctic is losing ice on every metric that scientists measure.\n\n---\n*Sources: NSIDC (https://nsidc.org), NASA (https://science.nasa.gov/earth/arctic-winter-sea-ice-2026/), NOAA Arctic Report Card 2025 (https://arctic.noaa.gov/report-card), UAF Geophysical Institute (https://www.gi.alaska.edu)*\n*Charts and analysis: Espresso Charts*\n\n**Tags:** climate, arctic, sea-ice, environment, nasa, data-visualization",
          "tags": "climate, arctic, sea-ice, environment, nasa",
          "publish_at": null
        },
        "substack_chart_notes": [
          {
            "day": "Fri",
            "text": "Arctic winter sea ice peaked at 14.29 million km squared on March 15, tying 2025 for the lowest maximum in the 48-year satellite record. In 1979, the maximum was 16.5 million km squared. The decline is steady, consistent, and accelerating in recent years.\n\nSubscribe for the full story: espressocharts.substack.com ☕",
            "image_asset": "story_2_chart_1.png"
          },
          {
            "day": "Sat",
            "text": "Over 95% of the Arctic's oldest, thickest sea ice, the multi-year ice older than four years, has vanished since the 1980s. The Arctic is not just losing coverage. It is losing the structural backbone that once kept the ice sheet resilient through summer melt seasons.\n\nSubscribe for the full story: espressocharts.substack.com ☕",
            "image_asset": "story_2_chart_3.png"
          },
          {
            "day": "Sun",
            "text": "Along Alaska's northern coast, the stable landfast ice season has shortened by weeks to months over 27 years. The ice forms later in fall and breaks up earlier in spring. For Indigenous communities, that means more dangerous travel and less time for subsistence hunting on safe ice.\n\nSubscribe for the full story: espressocharts.substack.com ☕",
            "image_asset": "story_2_chart_4.png"
          }
        ]
      },
      "poster": {
        "hero_number": "-13%",
        "hero_unit": "since 1979",
        "hero_eyebrow": "ARCTIC WINTER SEA ICE DECLINE",
        "insight_text": "Arctic winter sea ice peaked at its lowest\non record, for the second consecutive year.\nThe deficit is twice the size of Texas.",
        "insight_context": "In 1979, the winter maximum was 16.5 million\nkm². The decline averages 2.6% per decade but\nhas accelerated. The five lowest winter peaks\nhave all occurred in the last ten years.",
        "chart_x_labels": [
          [
            1979,
            "1979"
          ],
          [
            1990,
            "1990"
          ],
          [
            2000,
            "2000"
          ],
          [
            2010,
            "2010"
          ],
          [
            2026,
            "Now"
          ]
        ],
        "chart_y_labels": [
          14,
          15,
          16,
          17
        ],
        "chart_y_format": "{:.0f}M",
        "chart_color": "#3F5B83",
        "annotations": [
          {
            "year": "1979",
            "value": "16.5M km²",
            "desc": "Satellite record\nbegins",
            "color": "#4D5523",
            "chart_x": 1979,
            "chart_y": 16.5
          },
          {
            "year": "2015",
            "value": "14.7M km²",
            "desc": "Record low set,\nthen broken",
            "color": "#CDAF7B",
            "chart_x": 2015,
            "chart_y": 14.7
          },
          {
            "year": "2026",
            "value": "14.29M km²",
            "desc": "Tied record,\n2nd year running",
            "color": "#A14516",
            "chart_x": 2026,
            "chart_y": 14.29
          }
        ],
        "source_lines": [
          "SOURCE: NSIDC / NASA",
          "nsidc.org",
          "DATA DATE: 2026-03-26"
        ],
        "issue_number": "003",
        "issue_topic": "Arctic Sea Ice",
        "accent_color": "#A14516"
      }
    }
  ]
}
''')

# ===== BOX 2: AGENCY WISE + BAR CHART =====
                if all_roster_scheduled:
                    combined_roster = pd.concat(all_roster_scheduled, ignore_index=True)
                    combined_roster['3P'] = combined_roster['3P'].replace('QuessCorp', 'Quesscorp')

                    agency_data = []
                    for agency in sorted(combined_roster['3P'].dropna().unique()):
                        ag = combined_roster[combined_roster['3P'] == agency]
                        ag_hc = len(ag)
                        ag_sl = len(ag[ag['Attendance'] == 'SL'])
                        ag_abwi = len(ag[ag['Attendance'] == 'ABWI'])
                        ag_ab = len(ag[ag['Attendance'] == 'AB'])
                        ag_upl = ag_sl + ag_abwi + ag_ab
                        ag_pl = len(ag[ag['Attendance'] == 'PL'])
                        ag_upl_trend = round((ag_upl / ag_hc) * 100, 2) if ag_hc > 0 else 0
                        ag_pl_trend = round((ag_pl / ag_hc) * 100, 2) if ag_hc > 0 else 0

                        agency_data.append({
                            'Agency': agency,
                            'Week No': week_no,
                            'Total HC': ag_hc,
                            'SL': ag_sl,
                            'ABWI': ag_abwi,
                            'NCNS': ag_ab,
                            'Total UPLs': ag_upl,
                            'Trend': f'{ag_upl_trend:.2f}%',
                            'Total PLs': ag_pl,
                            'PL Trend': f'{ag_pl_trend:.2f}%',
                        })

                    agency_df_display = pd.DataFrame(agency_data)

                    ag_t_hc = t_hc  
                    ag_t_sl = agency_df_display['SL'].sum()
                    ag_t_abwi = agency_df_display['ABWI'].sum()
                    ag_t_ncns = agency_df_display['NCNS'].sum()
                    ag_t_upl = agency_df_display['Total UPLs'].sum()
                    ag_t_pl = agency_df_display['Total PLs'].sum()
                    ag_t_upl_trend = round((ag_t_upl / ag_t_hc) * 100, 2) if ag_t_hc > 0 else 0
                    ag_t_pl_trend = round((ag_t_pl / ag_t_hc) * 100, 2) if ag_t_hc > 0 else 0

                    ag_total_row = pd.DataFrame([{
                        'Agency': 'Total',
                        'Week No': week_no,
                        'Total HC': ag_t_hc,
                        'SL': ag_t_sl,
                        'ABWI': ag_t_abwi,
                        'NCNS': ag_t_ncns,
                        'Total UPLs': ag_t_upl,
                        'Trend': f'{ag_t_upl_trend:.2f}%',
                        'Total PLs': ag_t_pl,
                        'PL Trend': f'{ag_t_pl_trend:.2f}%',
                    }])
                    agency_df_display = pd.concat([agency_df_display, ag_total_row], ignore_index=True)

                    ag_left, ag_right = st.columns([6, 4])

                    with ag_left:
                        st.markdown("**Agency wise:-**")
                        ag_html = '<table style="border-collapse:collapse; width:100%; font-size:11px; font-family:sans-serif;">'
                        ag_cols = ['Agency','Week No','Total HC','SL','ABWI','NCNS','Total UPLs','Trend','Total PLs','PL Trend']
                        ag_hdr_colors = ['#00695c','#00695c','#0d47a1','#e65100','#e65100','#e65100','#b71c1c','#2e7d32','#1565c0','#2e7d32']
                        ag_html += '<tr>'
                        for idx_h, col in enumerate(ag_cols):
                            ag_html += f'<td style="padding:5px 6px; background:{ag_hdr_colors[idx_h]}; color:white; font-weight:700; text-align:center; border:1px solid #ddd; white-space:nowrap;">{col}</td>'
                        ag_html += '</tr>'
                        for row_idx in range(len(agency_df_display)):
                            is_total = agency_df_display.iloc[row_idx]['Agency'] == 'Total'
                            bg = '#fff9c4' if is_total else ('#f1f8e9' if row_idx % 2 == 0 else '#ffffff')
                            fw = '700' if is_total else '500'
                            ag_html += f'<tr style="background:{bg};">'
                            for col in ag_cols:
                                val = agency_df_display.iloc[row_idx][col]
                                cell_bg = ''
                                if col == 'Trend' and not is_total:
                                    try:
                                        tv = float(str(val).replace('%',''))
                                        if tv <= 3.00: cell_bg = 'background:#c8e6c9;'
                                        elif tv <= 5.00: cell_bg = 'background:#fff9c4;'
                                        else: cell_bg = 'background:#ffcdd2;'
                                    except: pass
                                if col == 'PL Trend' and not is_total:
                                    try:
                                        tv = float(str(val).replace('%',''))
                                        if tv <= 9.67: cell_bg = 'background:#c8e6c9;'
                                        elif tv <= 11.00: cell_bg = 'background:#fff9c4;'
                                        else: cell_bg = 'background:#ffcdd2;'
                                    except: pass
                                ag_html += f'<td style="padding:4px 6px; text-align:center; border:1px solid #ddd; font-weight:{fw}; {cell_bg} white-space:nowrap;">{val}</td>'
                            ag_html += '</tr>'
                        ag_html += '</table>'
                        st.markdown(ag_html, unsafe_allow_html=True)

                    with ag_right:
                        st.markdown("#### 📊 Agency UPL Share")
                        chart_data = agency_df_display[agency_df_display['Agency'] != 'Total'][['Agency', 'Total UPLs']].copy()
                        chart_data = chart_data.sort_values('Total UPLs', ascending=False).reset_index(drop=True)

                        gradient_colors = ['#b71c1c', '#e53935', '#f57c00', '#fdd835', '#81c784', '#2e7d32']
                        num_bars = len(chart_data)
                        bar_colors = gradient_colors[:num_bars] if num_bars <= len(gradient_colors) else gradient_colors

                        chart_data['Color'] = bar_colors[:num_bars]
                        agency_order = chart_data['Agency'].tolist()

                        bar_chart = alt.Chart(chart_data).mark_bar(
                            cornerRadiusTopLeft=6,
                            cornerRadiusTopRight=6,
                            size=28,
                        ).encode(
                            x=alt.X('Agency:N', sort=agency_order, axis=alt.Axis(labelAngle=-45, labelFontSize=10)),
                            y=alt.Y('Total UPLs:Q', title='Total UPL Count'),
                            color=alt.Color('Agency:N', legend=None, scale=alt.Scale(
                                domain=agency_order,
                                range=bar_colors[:num_bars]
                            )),
                            tooltip=['Agency', 'Total UPLs']
                        ).properties(height=320)
                        st.altair_chart(bar_chart, use_container_width=True)

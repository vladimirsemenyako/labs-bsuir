import folium
import plotly.graph_objects as go
import plotly.express as px
import pandas as pd
from typing import Dict
from src.config import RIVERS_BY, RIVER_COLORS

class MapVisualizer:
    def __init__(self):
        self.rivers = RIVERS_BY
        self.colors = RIVER_COLORS
    
    def create_belarus_map(self, entity_data: Dict[str, float], title: str = "") -> folium.Map:
        m = folium.Map(
            location=[53.5, 28.0],
            zoom_start=7,
            tiles='OpenStreetMap'
        )
        
        if not entity_data:
            return m
        
        values = list(entity_data.values())
        min_val = min(values)
        max_val = max(values)
        value_range = max_val - min_val if max_val != min_val else 1
        
        for entity, coords in self.rivers.items():
            value = entity_data.get(entity, None)
            if value is None:
                continue
            
            normalized = (value - min_val) / value_range if value_range > 0 else 0.5
            color = self.colors.get(entity, '#808080')
            
            folium.CircleMarker(
                location=[coords['lat'], coords['lon']],
                radius=15 + normalized * 20,
                popup=f"<b>{entity}</b><br>{title}: {value:.3f}",
                tooltip=f"{entity}: {value:.3f}",
                color=color,
                fill=True,
                fillColor=color,
                fillOpacity=0.6,
                weight=2
            ).add_to(m)
            
            folium.Marker(
                location=[coords['lat'], coords['lon']],
                icon=folium.DivIcon(html=f"""
                    <div style="font-size: 9pt; color: white; font-weight: bold; 
                                text-shadow: 1px 1px 3px black; background: rgba(0,0,0,0.5); 
                                padding: 2px 5px; border-radius: 3px;">
                        {entity}: {value:.2f}
                    </div>
                """)
            ).add_to(m)
        
        return m
    
    def create_timeseries_plot(self, historical: pd.DataFrame, 
                               forecast: pd.DataFrame = None,
                               title: str = "") -> go.Figure:
        fig = go.Figure()
        
        fig.add_trace(go.Scatter(
            x=historical['year'],
            y=historical['value'],
            mode='lines+markers',
            name='Исторические данные',
            line=dict(color='#2E86AB', width=2),
            marker=dict(size=6)
        ))
        
        if forecast is not None and not forecast.empty:
            future_data = forecast[forecast['year'] > historical['year'].max()]
            
            if not future_data.empty:
                fig.add_trace(go.Scatter(
                    x=future_data['year'],
                    y=future_data['forecast'],
                    mode='lines+markers',
                    name='Прогноз',
                    line=dict(color='#A23B72', width=2, dash='dash'),
                    marker=dict(size=6)
                ))
                
                fig.add_trace(go.Scatter(
                    x=future_data['year'].tolist() + future_data['year'].tolist()[::-1],
                    y=future_data['upper'].tolist() + future_data['lower'].tolist()[::-1],
                    fill='toself',
                    fillcolor='rgba(162, 59, 114, 0.2)',
                    line=dict(color='rgba(255,255,255,0)'),
                    name='Доверительный интервал',
                    showlegend=True
                ))
        
        fig.update_layout(
            title=title,
            xaxis_title='Год',
            yaxis_title='Значение',
            hovermode='x unified',
            template='plotly_white',
            height=500
        )
        
        return fig
    
    def create_entity_comparison(self, data: Dict[str, pd.DataFrame], 
                                   year: int) -> go.Figure:
        entities = []
        values = []
        
        for entity, df in data.items():
            entity_data = df[df['year'].dt.year == year]
            if not entity_data.empty:
                entities.append(entity)
                values.append(entity_data['value'].values[0])
        
        fig = go.Figure(data=[
            go.Bar(
                x=entities,
                y=values,
                marker_color=[self.colors.get(e, '#808080') for e in entities]
            )
        ])
        
        fig.update_layout(
            title=f'Сравнение ({year} год)',
            xaxis_title='Объект',
            yaxis_title='Значение',
            template='plotly_white',
            height=400,
            xaxis_tickangle=-45
        )
        
        return fig


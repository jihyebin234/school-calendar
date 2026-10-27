import { useEffect } from 'react'
import { CircleMarker, MapContainer, Popup, TileLayer, useMap, useMapEvents } from 'react-leaflet'
import 'leaflet/dist/leaflet.css'

function MapView({ center, onSelect }) {
  const map = useMap()
  const latitude = center?.[0]
  const longitude = center?.[1]

  useMapEvents({
    click(event) {
      onSelect([event.latlng.lat, event.latlng.lng])
    },
  })

  useEffect(() => {
    if (latitude != null && longitude != null) map.setView([latitude, longitude], Math.max(map.getZoom(), 14))
  }, [latitude, longitude, map])
  return null
}

export default function LocationMap({ center, selected, onSelect }) {
  return (
    <MapContainer
      center={center}
      zoom={selected ? 14 : 12}
      scrollWheelZoom={false}
      className="location-map"
    >
      <TileLayer
        attribution='&copy; <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a> contributors'
        url="https://tile.openstreetmap.org/{z}/{x}/{y}.png"
      />
      <MapView center={center} onSelect={onSelect} />
      {selected && (
        <CircleMarker center={selected} radius={8} pathOptions={{ color: '#326650', fillColor: '#477c67', fillOpacity: 0.9 }}>
          <Popup>선택한 위치</Popup>
        </CircleMarker>
      )}
    </MapContainer>
  )
}

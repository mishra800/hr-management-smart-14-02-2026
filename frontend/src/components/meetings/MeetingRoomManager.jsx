import { useState, useEffect } from 'react';
import api from '../../api/axios';
import { useToast } from '../../hooks/usetoast';

export default function MeetingRoomManager() {
  const [rooms, setRooms] = useState([]);
  const [bookings, setBookings] = useState([]);
  const [loading, setLoading] = useState(true);
  const [showCreateRoomModal, setShowCreateRoomModal] = useState(false);
  const [showBookingModal, setShowBookingModal] = useState(false);
  const [selectedRoom, setSelectedRoom] = useState(null);
  const { showToast } = useToast();

  const [newRoom, setNewRoom] = useState({
    name: '',
    location: '',
    capacity: 10,
    equipment: []
  });

  const [newBooking, setNewBooking] = useState({
    room_id: '',
    meeting_date: '',
    start_time: '09:00',
    end_time: '10:00',
    purpose: '',
    attendee_count: 1
  });

  const equipmentOptions = [
    'Projector', 'Whiteboard', 'TV Screen', 'Conference Phone', 
    'Video Conferencing', 'Microphone', 'Speakers', 'Flipchart'
  ];

  useEffect(() => {
    fetchRooms();
    fetchBookings();
  }, []);

  const fetchRooms = async () => {
    try {
      const response = await api.get('/meeting-rooms/');
      setRooms(response.data);
    } catch (error) {
      console.error('Error fetching rooms:', error);
      showToast('Failed to load meeting rooms', 'error');
    }
  };

  const fetchBookings = async () => {
    try {
      const response = await api.get('/meeting-rooms/bookings');
      setBookings(response.data);
    } catch (error) {
      console.error('Error fetching bookings:', error);
    } finally {
      setLoading(false);
    }
  };

  const handleCreateRoom = async (e) => {
    e.preventDefault();
    try {
      await api.post('/meeting-rooms/', newRoom);
      showToast('Meeting room created successfully', 'success');
      setShowCreateRoomModal(false);
      resetNewRoom();
      fetchRooms();
    } catch (error) {
      console.error('Error creating room:', error);
      showToast('Failed to create meeting room', 'error');
    }
  };

  const handleBookRoom = async (e) => {
    e.preventDefault();
    try {
      await api.post('/meeting-rooms/bookings', newBooking);
      showToast('Room booked successfully', 'success');
      setShowBookingModal(false);
      resetNewBooking();
      fetchBookings();
    } catch (error) {
      console.error('Error booking room:', error);
      showToast('Failed to book room', 'error');
    }
  };

  const resetNewRoom = () => {
    setNewRoom({
      name: '',
      location: '',
      capacity: 10,
      equipment: []
    });
  };

  const resetNewBooking = () => {
    setNewBooking({
      room_id: '',
      meeting_date: '',
      start_time: '09:00',
      end_time: '10:00',
      purpose: '',
      attendee_count: 1
    });
  };

  const handleEquipmentChange = (equipment) => {
    setNewRoom(prev => ({
      ...prev,
      equipment: prev.equipment.includes(equipment)
        ? prev.equipment.filter(e => e !== equipment)
        : [...prev.equipment, equipment]
    }));
  };

  if (loading) {
    return (
      <div className="flex justify-center items-center h-64">
        <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-600"></div>
      </div>
    );
  }

  return (
    <div className="space-y-6">
      <div className="flex justify-between items-center">
        <h2 className="text-2xl font-bold text-gray-800">Meeting Room Management</h2>
        <div className="flex gap-2">
          <button
            onClick={() => setShowCreateRoomModal(true)}
            className="px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700"
          >
            Add Room
          </button>
          <button
            onClick={() => setShowBookingModal(true)}
            className="px-4 py-2 bg-green-600 text-white rounded-lg hover:bg-green-700"
          >
            Book Room
          </button>
        </div>
      </div>

      {/* Rooms Grid */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
        {rooms.map((room) => (
          <div key={room.id} className="bg-white rounded-lg shadow-md p-6">
            <div className="flex justify-between items-start mb-4">
              <h3 className="text-lg font-semibold text-gray-800">{room.name}</h3>
              <span className={`px-2 py-1 text-xs rounded ${
                room.is_active ? 'bg-green-100 text-green-800' : 'bg-red-100 text-red-800'
              }`}>
                {room.is_active ? 'Active' : 'Inactive'}
              </span>
            </div>
            
            <div className="space-y-2 text-sm text-gray-600">
              <p><span className="font-medium">Location:</span> {room.location}</p>
              <p><span className="font-medium">Capacity:</span> {room.capacity} people</p>
              
              {room.equipment && room.equipment.length > 0 && (
                <div>
                  <span className="font-medium">Equipment:</span>
                  <div className="flex flex-wrap gap-1 mt-1">
                    {room.equipment.map((eq, index) => (
                      <span key={index} className="px-2 py-1 bg-blue-100 text-blue-800 text-xs rounded">
                        {eq}
                      </span>
                    ))}
                  </div>
                </div>
              )}
            </div>

            <button
              onClick={() => {
                setSelectedRoom(room);
                setNewBooking(prev => ({ ...prev, room_id: room.id }));
                setShowBookingModal(true);
              }}
              className="mt-4 w-full px-3 py-2 bg-blue-600 text-white rounded hover:bg-blue-700"
            >
              Book This Room
            </button>
          </div>
        ))}
      </div>

      {rooms.length === 0 && (
        <div className="text-center py-12 text-gray-500">
          <svg className="w-16 h-16 mx-auto mb-4 text-gray-300" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M19 21V5a2 2 0 00-2-2H7a2 2 0 00-2 2v16m14 0h2m-2 0h-5m-9 0H3m2 0h5M9 7h1m-1 4h1m4-4h1m-1 4h1m-5 10v-5a1 1 0 011-1h2a1 1 0 011 1v5m-4 0h4" />
          </svg>
          <p className="text-lg font-medium">No meeting rooms available</p>
          <p className="text-sm">Add your first meeting room to get started</p>
        </div>
      )}

      {/* Recent Bookings */}
      <div className="bg-white rounded-lg shadow-md p-6">
        <h3 className="text-lg font-semibold text-gray-800 mb-4">Recent Bookings</h3>
        <div className="space-y-3">
          {bookings.slice(0, 5).map((booking) => (
            <div key={booking.id} className="flex justify-between items-center p-3 bg-gray-50 rounded">
              <div>
                <p className="font-medium">{rooms.find(r => r.id === booking.room_id)?.name}</p>
                <p className="text-sm text-gray-600">
                  {booking.meeting_date} • {booking.start_time} - {booking.end_time}
                </p>
                <p className="text-sm text-gray-500">{booking.purpose}</p>
              </div>
              <span className={`px-2 py-1 text-xs rounded ${
                booking.status === 'confirmed' ? 'bg-green-100 text-green-800' : 
                booking.status === 'cancelled' ? 'bg-red-100 text-red-800' :
                'bg-yellow-100 text-yellow-800'
              }`}>
                {booking.status}
              </span>
            </div>
          ))}
        </div>
      </div>

      {/* Create Room Modal */}
      {showCreateRoomModal && (
        <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50">
          <div className="bg-white rounded-lg p-6 w-full max-w-md">
            <div className="flex justify-between items-center mb-6">
              <h2 className="text-xl font-bold text-gray-800">Add Meeting Room</h2>
              <button
                onClick={() => setShowCreateRoomModal(false)}
                className="text-gray-500 hover:text-gray-700"
              >
                <svg className="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M6 18L18 6M6 6l12 12" />
                </svg>
              </button>
            </div>

            <form onSubmit={handleCreateRoom} className="space-y-4">
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-2">Room Name *</label>
                <input
                  type="text"
                  required
                  value={newRoom.name}
                  onChange={(e) => setNewRoom({...newRoom, name: e.target.value})}
                  className="w-full p-2 border border-gray-300 rounded-md focus:ring-2 focus:ring-blue-500"
                  placeholder="Conference Room A"
                />
              </div>

              <div>
                <label className="block text-sm font-medium text-gray-700 mb-2">Location</label>
                <input
                  type="text"
                  value={newRoom.location}
                  onChange={(e) => setNewRoom({...newRoom, location: e.target.value})}
                  className="w-full p-2 border border-gray-300 rounded-md focus:ring-2 focus:ring-blue-500"
                  placeholder="2nd Floor, Building A"
                />
              </div>

              <div>
                <label className="block text-sm font-medium text-gray-700 mb-2">Capacity</label>
                <input
                  type="number"
                  min="1"
                  value={newRoom.capacity}
                  onChange={(e) => setNewRoom({...newRoom, capacity: parseInt(e.target.value)})}
                  className="w-full p-2 border border-gray-300 rounded-md focus:ring-2 focus:ring-blue-500"
                />
              </div>

              <div>
                <label className="block text-sm font-medium text-gray-700 mb-2">Equipment</label>
                <div className="grid grid-cols-2 gap-2">
                  {equipmentOptions.map((equipment) => (
                    <label key={equipment} className="flex items-center">
                      <input
                        type="checkbox"
                        checked={newRoom.equipment.includes(equipment)}
                        onChange={() => handleEquipmentChange(equipment)}
                        className="mr-2"
                      />
                      <span className="text-sm">{equipment}</span>
                    </label>
                  ))}
                </div>
              </div>

              <div className="flex gap-3 pt-4">
                <button
                  type="submit"
                  className="flex-1 bg-blue-600 text-white py-2 px-4 rounded-md hover:bg-blue-700"
                >
                  Create Room
                </button>
                <button
                  type="button"
                  onClick={() => setShowCreateRoomModal(false)}
                  className="px-4 py-2 border border-gray-300 text-gray-700 rounded-md hover:bg-gray-50"
                >
                  Cancel
                </button>
              </div>
            </form>
          </div>
        </div>
      )}

      {/* Book Room Modal */}
      {showBookingModal && (
        <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50">
          <div className="bg-white rounded-lg p-6 w-full max-w-md">
            <div className="flex justify-between items-center mb-6">
              <h2 className="text-xl font-bold text-gray-800">Book Meeting Room</h2>
              <button
                onClick={() => setShowBookingModal(false)}
                className="text-gray-500 hover:text-gray-700"
              >
                <svg className="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M6 18L18 6M6 6l12 12" />
                </svg>
              </button>
            </div>

            <form onSubmit={handleBookRoom} className="space-y-4">
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-2">Room *</label>
                <select
                  required
                  value={newBooking.room_id}
                  onChange={(e) => setNewBooking({...newBooking, room_id: parseInt(e.target.value)})}
                  className="w-full p-2 border border-gray-300 rounded-md focus:ring-2 focus:ring-blue-500"
                >
                  <option value="">Select a room</option>
                  {rooms.filter(room => room.is_active).map((room) => (
                    <option key={room.id} value={room.id}>
                      {room.name} (Capacity: {room.capacity})
                    </option>
                  ))}
                </select>
              </div>

              <div>
                <label className="block text-sm font-medium text-gray-700 mb-2">Date *</label>
                <input
                  type="date"
                  required
                  value={newBooking.meeting_date}
                  onChange={(e) => setNewBooking({...newBooking, meeting_date: e.target.value})}
                  className="w-full p-2 border border-gray-300 rounded-md focus:ring-2 focus:ring-blue-500"
                />
              </div>

              <div className="grid grid-cols-2 gap-4">
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-2">Start Time *</label>
                  <input
                    type="time"
                    required
                    value={newBooking.start_time}
                    onChange={(e) => setNewBooking({...newBooking, start_time: e.target.value})}
                    className="w-full p-2 border border-gray-300 rounded-md focus:ring-2 focus:ring-blue-500"
                  />
                </div>
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-2">End Time *</label>
                  <input
                    type="time"
                    required
                    value={newBooking.end_time}
                    onChange={(e) => setNewBooking({...newBooking, end_time: e.target.value})}
                    className="w-full p-2 border border-gray-300 rounded-md focus:ring-2 focus:ring-blue-500"
                  />
                </div>
              </div>

              <div>
                <label className="block text-sm font-medium text-gray-700 mb-2">Purpose</label>
                <input
                  type="text"
                  value={newBooking.purpose}
                  onChange={(e) => setNewBooking({...newBooking, purpose: e.target.value})}
                  className="w-full p-2 border border-gray-300 rounded-md focus:ring-2 focus:ring-blue-500"
                  placeholder="Team meeting, client presentation, etc."
                />
              </div>

              <div>
                <label className="block text-sm font-medium text-gray-700 mb-2">Expected Attendees</label>
                <input
                  type="number"
                  min="1"
                  value={newBooking.attendee_count}
                  onChange={(e) => setNewBooking({...newBooking, attendee_count: parseInt(e.target.value)})}
                  className="w-full p-2 border border-gray-300 rounded-md focus:ring-2 focus:ring-blue-500"
                />
              </div>

              <div className="flex gap-3 pt-4">
                <button
                  type="submit"
                  className="flex-1 bg-green-600 text-white py-2 px-4 rounded-md hover:bg-green-700"
                >
                  Book Room
                </button>
                <button
                  type="button"
                  onClick={() => setShowBookingModal(false)}
                  className="px-4 py-2 border border-gray-300 text-gray-700 rounded-md hover:bg-gray-50"
                >
                  Cancel
                </button>
              </div>
            </form>
          </div>
        </div>
      )}
    </div>
  );
}
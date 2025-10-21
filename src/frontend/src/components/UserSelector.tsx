import React, { useState, useEffect } from 'react'
import { api, User } from '../services/api'
import { showToast, LoadingSpinner } from '.'

interface UserSelectorProps {
  selectedIds: number[]
  onChange: (selectedIds: number[]) => void
}

const UserSelector: React.FC<UserSelectorProps> = ({ selectedIds, onChange }) => {
  const [users, setUsers] = useState<User[]>([])
  const [loading, setLoading] = useState(true)
  const [searchQuery, setSearchQuery] = useState('')

  useEffect(() => {
    fetchUsers()
  }, [])

  const fetchUsers = async () => {
    try {
      const response = await api.getAllUsers()
      if (response.success) {
        setUsers(response.data)
      }
    } catch (error) {
      showToast({
        type: 'error',
        message: '無法載入使用者列表',
        autoClose: 3000
      })
    } finally {
      setLoading(false)
    }
  }

  const toggleUser = (userId: number) => {
    if (selectedIds.includes(userId)) {
      onChange(selectedIds.filter(id => id !== userId))
    } else {
      onChange([...selectedIds, userId])
    }
  }

  const filteredUsers = users.filter(user =>
    user.name.toLowerCase().includes(searchQuery.toLowerCase()) ||
    user.email.toLowerCase().includes(searchQuery.toLowerCase())
  )

  const handleSelectAll = () => {
    const allFilteredIds = filteredUsers.map(user => Number(user.id))
    onChange(allFilteredIds)
  }

  const handleDeselectAll = () => {
    onChange([])
  }

  const isAllSelected = filteredUsers.length > 0 &&
    filteredUsers.every(user => selectedIds.includes(Number(user.id)))

  if (loading) {
    return (
      <div className="flex justify-center py-8">
        <LoadingSpinner />
      </div>
    )
  }

  return (
    <div className="space-y-3">
      {/* Search */}
      <input
        type="text"
        placeholder="搜尋使用者（姓名或Email）"
        value={searchQuery}
        onChange={(e) => setSearchQuery(e.target.value)}
        className="w-full px-4 py-2 border border-gray-300 dark:border-gray-600 rounded-lg focus:ring-2 focus:ring-blue-500 dark:bg-gray-700 dark:text-white"
      />

      {/* Select All / Deselect All */}
      <div className="flex items-center justify-between">
        <button
          type="button"
          onClick={handleSelectAll}
          disabled={filteredUsers.length === 0}
          className="text-sm text-blue-600 dark:text-blue-400 hover:text-blue-700 dark:hover:text-blue-300 disabled:text-gray-400 disabled:cursor-not-allowed"
        >
          ✓ 全選
        </button>
        <button
          type="button"
          onClick={handleDeselectAll}
          disabled={selectedIds.length === 0}
          className="text-sm text-gray-600 dark:text-gray-400 hover:text-gray-700 dark:hover:text-gray-300 disabled:text-gray-400 disabled:cursor-not-allowed"
        >
          ✗ 全不選
        </button>
      </div>

      {/* User List */}
      <div className="max-h-60 overflow-y-auto border border-gray-200 dark:border-gray-600 rounded-lg">
        {filteredUsers.length === 0 ? (
          <div className="text-center py-8 text-gray-500">
            {searchQuery ? '沒有符合的使用者' : '沒有可用使用者'}
          </div>
        ) : (
          <div className="divide-y divide-gray-200 dark:divide-gray-600">
            {filteredUsers.map((user) => (
              <label
                key={user.id}
                className="flex items-center p-3 hover:bg-gray-50 dark:hover:bg-gray-700 cursor-pointer transition-colors"
              >
                <input
                  type="checkbox"
                  checked={selectedIds.includes(Number(user.id))}
                  onChange={() => toggleUser(Number(user.id))}
                  className="w-4 h-4 text-blue-600 border-gray-300 rounded focus:ring-blue-500"
                />
                <div className="ml-3 flex-1">
                  <div className="text-sm font-medium text-gray-900 dark:text-white">
                    {user.name}
                  </div>
                  <div className="text-xs text-gray-500 dark:text-gray-400">
                    {user.email}
                  </div>
                </div>
                {user.role === 'admin' && (
                  <span className="text-xs bg-blue-100 dark:bg-blue-900 text-blue-800 dark:text-blue-200 px-2 py-1 rounded">
                    管理員
                  </span>
                )}
              </label>
            ))}
          </div>
        )}
      </div>

      {/* Selected Count */}
      <div className="text-sm text-gray-600 dark:text-gray-400">
        已選擇 {selectedIds.length} 位參與者
      </div>
    </div>
  )
}

export default UserSelector

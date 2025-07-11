import React from "react";
import { useUser } from "../../context/UserContext";
import { Menu } from "@headlessui/react";
import { User as UserIcon } from "lucide-react";
import { useNavigate } from "react-router-dom";

export default function Topbar() {
  const { user, logout } = useUser();
  const navigate = useNavigate();

  return (
    <div className="flex items-center justify-end h-16 px-6 border-b border-gray-200 bg-white">
      {user && (
        <Menu as="div" className="relative">
          <Menu.Button className="flex items-center space-x-2 focus:outline-none">
            <UserIcon className="w-6 h-6 text-gray-700" />
            <span className="text-gray-700 font-medium">{user.username}</span>
          </Menu.Button>
          <Menu.Items className="absolute right-0 mt-2 w-64 bg-white border border-gray-200 rounded-md shadow-lg z-50">
            <div className="px-4 py-3 border-b border-gray-100">
              <div className="font-semibold text-gray-900">{user.username}</div>
              <div className="text-xs text-gray-500">{user.role}</div>
              <div className="text-xs text-gray-500">{user.email}</div>
            </div>
            <Menu.Item>
              {({ active }) => (
                <button
                  className={`w-full text-left px-4 py-2 ${active ? "bg-gray-100" : ""}`}
                  onClick={() => navigate("/profile")}
                >
                  Your Profile
                </button>
              )}
            </Menu.Item>
            <Menu.Item>
              {({ active }) => (
                <button
                  className={`w-full text-left px-4 py-2 text-red-600 ${active ? "bg-gray-100" : ""}`}
                  onClick={logout}
                >
                  Sign Out
                </button>
              )}
            </Menu.Item>
          </Menu.Items>
        </Menu>
      )}
    </div>
  );
} 
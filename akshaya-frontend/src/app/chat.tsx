import { Redirect, useLocalSearchParams } from "expo-router";

export default function ChatRedirect() {
  const params = useLocalSearchParams<{
    query?: string | string[];
  }>();

  return (
    <Redirect
      href={{
        pathname: "/",
        params,
      }}
    />
  );
}
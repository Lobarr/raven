export enum ServiceState {
  BROKEN,
  DOWN,
  UP,
  OFF
}

export type Service = {
  _id: string;
  path: string;
  state: ServiceState;
  secure: boolean;
  targets: string[];
  cur_target_index: number;
  whitelisted_hosts: string[];
  blacklisted_hosts: string[];
  public_key: string;
}
